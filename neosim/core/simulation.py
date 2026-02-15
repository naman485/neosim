"""
Simulation Engine

Orchestrates the multi-agent GTM simulation.
Runs cycles, aggregates results, produces final output.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import time
import uuid

from .config import NeoSimConfig, _config_to_dict
from .metrics import MetricsAggregator, SimulationMetrics
from ..agents.base import AgentResponse, LLMProvider
from ..agents.buyer import BuyerAgent, create_buyer_agents
from ..agents.competitor import CompetitorAgent, create_competitor_agents
from ..agents.channel import ChannelAgent, create_channel_agents
from ..agents.advisor import AdvisorAgent


@dataclass
class CycleResult:
    """Results from a single simulation cycle."""
    cycle: int
    buyer_responses: List[AgentResponse]
    competitor_responses: List[AgentResponse]
    channel_responses: List[AgentResponse]
    advisor_response: Optional[AgentResponse]
    metrics: Dict[str, Any]
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class SimulationResult:
    """Complete simulation results."""
    sim_id: str
    config: NeoSimConfig
    cycles: List[CycleResult]
    final_metrics: SimulationMetrics
    started_at: str
    completed_at: str
    total_duration_seconds: float

    # Summary fields populated after simulation
    overall_assessment: str = ""
    confidence_score: float = 0.0
    top_recommendations: List[str] = field(default_factory=list)
    top_risks: List[str] = field(default_factory=list)


class Simulation:
    """
    Main simulation orchestrator.

    Coordinates all agent types through simulation cycles
    and aggregates results into actionable insights.
    """

    def __init__(
        self,
        config: NeoSimConfig,
        provider: LLMProvider = LLMProvider.ANTHROPIC,
        on_cycle_complete: Optional[Callable[[int, CycleResult], None]] = None,
    ):
        """
        Initialize simulation.

        Args:
            config: NeoSim configuration
            provider: LLM provider to use
            on_cycle_complete: Callback after each cycle (for progress reporting)
        """
        self.config = config
        self.provider = provider
        self.on_cycle_complete = on_cycle_complete

        self.sim_id = str(uuid.uuid4())[:8]
        self.metrics_aggregator = MetricsAggregator()

        # Initialize agents
        self._init_agents()

    def _init_agents(self) -> None:
        """Initialize all agent instances."""
        # Convert config objects to dicts for agent creation
        icp_dicts = [
            {
                "name": p.name,
                "role": p.role,
                "company_size": p.company_size,
                "pain_points": p.pain_points,
                "goals": p.goals,
                "budget_range": p.budget_range,
                "decision_speed": p.decision_speed,
                "objection_tendencies": p.objection_tendencies,
            }
            for p in self.config.icp_personas
        ]

        competitor_dicts = [
            {
                "name": c.name,
                "positioning": c.positioning,
                "pricing": c.pricing,
                "strengths": c.strengths,
                "weaknesses": c.weaknesses,
                "market_share": c.market_share,
            }
            for c in self.config.competitors
        ]

        channel_dicts = [
            {
                "name": c.name,
                "priority": c.priority,
                "budget_allocation": c.budget_allocation,
                "existing_presence": c.existing_presence,
                "strategy_notes": c.strategy_notes,
            }
            for c in self.config.channels
        ]

        # Calculate agents per persona to hit target
        buyer_count = self.config.simulation.buyer_agents
        personas_count = len(icp_dicts) or 1
        agents_per_persona = max(1, buyer_count // personas_count)

        self.buyer_agents = create_buyer_agents(
            icp_dicts or [{"name": "Default Buyer", "role": "Decision Maker"}],
            count_per_persona=agents_per_persona,
            provider=self.provider,
        )

        self.competitor_agents = create_competitor_agents(
            competitor_dicts or [{"name": "Generic Competitor"}],
            provider=self.provider,
        )

        self.channel_agents = create_channel_agents(
            channel_dicts or [{"name": "organic-social"}],
            provider=self.provider,
        )

        self.advisor_agent = AdvisorAgent(provider=self.provider)

    def run(self) -> SimulationResult:
        """
        Run the full simulation.

        Returns:
            Complete SimulationResult with all cycles and metrics
        """
        started_at = datetime.now()
        cycles = []

        # Build base context from config
        base_context = self._build_base_context()

        # Run simulation cycles
        total_cycles = self.config.simulation.cycles
        for cycle_num in range(1, total_cycles + 1):
            cycle_result = self._run_cycle(cycle_num, base_context)
            cycles.append(cycle_result)

            # Update metrics aggregator
            self.metrics_aggregator.add_cycle(cycle_result)

            # Callback for progress reporting
            if self.on_cycle_complete:
                self.on_cycle_complete(cycle_num, cycle_result)

        completed_at = datetime.now()
        duration = (completed_at - started_at).total_seconds()

        # Compute final metrics
        final_metrics = self.metrics_aggregator.compute_final_metrics()

        # Build result
        result = SimulationResult(
            sim_id=self.sim_id,
            config=self.config,
            cycles=cycles,
            final_metrics=final_metrics,
            started_at=started_at.isoformat(),
            completed_at=completed_at.isoformat(),
            total_duration_seconds=duration,
        )

        # Populate summary from last advisor response
        if cycles and cycles[-1].advisor_response:
            advisor = cycles[-1].advisor_response
            result.overall_assessment = advisor.decision
            result.confidence_score = advisor.confidence
            result.top_recommendations = [
                s.replace("recommendation:", "")
                for s in advisor.signals if s.startswith("recommendation:")
            ][:5]
            result.top_risks = [
                s.replace("risk:", "")
                for s in advisor.signals if s.startswith("risk:")
            ][:3]

        return result

    def _build_base_context(self) -> Dict[str, Any]:
        """Build base context dict from config."""
        return {
            "product": {
                "name": self.config.product.name,
                "description": self.config.product.description,
                "category": self.config.product.category,
                "stage": self.config.product.stage,
                "unique_value_prop": self.config.product.unique_value_prop,
                "key_features": self.config.product.key_features,
            },
            "pricing": {
                "model": self.config.pricing.model,
                "tiers": [
                    {"name": t.name, "price": t.price, "features": t.features}
                    for t in self.config.pricing.tiers
                ],
            },
            "icp_personas": [
                {
                    "name": p.name,
                    "role": p.role,
                    "company_size": p.company_size,
                    "pain_points": p.pain_points,
                    "goals": p.goals,
                }
                for p in self.config.icp_personas
            ],
            "channels": [
                {"name": c.name, "priority": c.priority}
                for c in self.config.channels
            ],
            "competitors": [
                {"name": c.name, "positioning": c.positioning}
                for c in self.config.competitors
            ],
        }

    def _run_cycle(self, cycle_num: int, base_context: Dict[str, Any]) -> CycleResult:
        """Run a single simulation cycle."""
        context = {**base_context, "cycle": cycle_num}

        # Run buyer agents
        buyer_responses = []
        for agent in self.buyer_agents:
            try:
                response = agent.decide(context)
                buyer_responses.append(response)
            except Exception as e:
                # Log error but continue
                buyer_responses.append(AgentResponse(
                    decision="ERROR",
                    reasoning=str(e),
                    confidence=0.0,
                ))

        # Run competitor agents
        competitor_responses = []
        for agent in self.competitor_agents:
            try:
                response = agent.decide(context)
                competitor_responses.append(response)
            except Exception as e:
                competitor_responses.append(AgentResponse(
                    decision="ERROR",
                    reasoning=str(e),
                    confidence=0.0,
                ))

        # Run channel agents
        channel_responses = []
        for agent in self.channel_agents:
            try:
                response = agent.decide(context)
                channel_responses.append(response)
            except Exception as e:
                channel_responses.append(AgentResponse(
                    decision="ERROR",
                    reasoning=str(e),
                    confidence=0.0,
                ))

        # Run advisor synthesis
        advisor_response = None
        try:
            advisor_response = self.advisor_agent.synthesize(
                context,
                buyer_responses,
                competitor_responses,
                channel_responses,
            )
        except Exception as e:
            advisor_response = AgentResponse(
                decision="ERROR",
                reasoning=str(e),
                confidence=0.0,
            )

        # Compute cycle metrics
        cycle_metrics = self._compute_cycle_metrics(
            buyer_responses, competitor_responses, channel_responses
        )

        return CycleResult(
            cycle=cycle_num,
            buyer_responses=buyer_responses,
            competitor_responses=competitor_responses,
            channel_responses=channel_responses,
            advisor_response=advisor_response,
            metrics=cycle_metrics,
        )

    def _compute_cycle_metrics(
        self,
        buyer_responses: List[AgentResponse],
        competitor_responses: List[AgentResponse],
        channel_responses: List[AgentResponse],
    ) -> Dict[str, Any]:
        """Compute aggregate metrics for a cycle."""
        # Buyer metrics
        buy_count = sum(1 for r in buyer_responses if r.decision == "BUY")
        total_buyers = len(buyer_responses)
        conversion_rate = buy_count / total_buyers if total_buyers > 0 else 0

        # Channel metrics
        cacs = [r.metrics.get("cac", 50) for r in channel_responses if r.metrics.get("cac")]
        avg_cac = sum(cacs) / len(cacs) if cacs else 50

        # Competitor metrics
        threat_levels = [
            r.metrics.get("threat_level", 5)
            for r in competitor_responses if r.metrics.get("threat_level")
        ]
        avg_threat = sum(threat_levels) / len(threat_levels) if threat_levels else 5

        return {
            "conversion_rate": conversion_rate,
            "buy_count": buy_count,
            "pass_count": sum(1 for r in buyer_responses if r.decision == "PASS"),
            "object_count": sum(1 for r in buyer_responses if r.decision == "OBJECT"),
            "avg_cac": avg_cac,
            "avg_competitor_threat": avg_threat,
            "avg_buyer_confidence": (
                sum(r.confidence for r in buyer_responses) / total_buyers
                if total_buyers > 0 else 0
            ),
        }

    def reset(self) -> None:
        """Reset simulation state for a new run."""
        self.sim_id = str(uuid.uuid4())[:8]
        self.metrics_aggregator = MetricsAggregator()

        # Reset all agents
        for agent in self.buyer_agents:
            agent.reset()
        for agent in self.competitor_agents:
            agent.reset()
        for agent in self.channel_agents:
            agent.reset()
        self.advisor_agent.reset()
