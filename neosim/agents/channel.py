"""
Channel Agent

Models channel-specific dynamics.
Simulates performance curves for each channel (organic, paid, community, outbound).
Outputs: CAC per channel, reach estimates, diminishing returns thresholds.
"""

import json
import re
from dataclasses import dataclass
from typing import Dict, Any, List
from .base import BaseAgent, AgentResponse, LLMProvider


@dataclass
class ChannelProfile:
    """Distribution channel characteristics."""
    name: str  # organic-social, paid-ads, community, outbound, seo, partnerships
    priority: int
    budget_allocation: float
    existing_presence: str  # none, minimal, moderate, strong
    strategy_notes: str


# Channel archetypes with typical characteristics
CHANNEL_ARCHETYPES = {
    "organic-social": {
        "typical_cac_range": (0, 50),
        "time_to_results": "medium",
        "scalability": "medium",
        "skill_required": "content creation, consistency",
    },
    "paid-ads": {
        "typical_cac_range": (20, 200),
        "time_to_results": "fast",
        "scalability": "high",
        "skill_required": "ad optimization, budget management",
    },
    "community": {
        "typical_cac_range": (0, 30),
        "time_to_results": "slow",
        "scalability": "low-medium",
        "skill_required": "community management, authenticity",
    },
    "outbound": {
        "typical_cac_range": (50, 500),
        "time_to_results": "medium",
        "scalability": "medium",
        "skill_required": "sales, personalization",
    },
    "seo": {
        "typical_cac_range": (10, 100),
        "time_to_results": "slow",
        "scalability": "high",
        "skill_required": "technical SEO, content strategy",
    },
    "partnerships": {
        "typical_cac_range": (0, 100),
        "time_to_results": "slow",
        "scalability": "variable",
        "skill_required": "relationship building, deal structuring",
    },
    "product-led": {
        "typical_cac_range": (0, 20),
        "time_to_results": "medium",
        "scalability": "high",
        "skill_required": "product design, virality mechanics",
    },
}


class ChannelAgent(BaseAgent):
    """
    Channel Agent - Models distribution channel dynamics.

    Each channel agent simulates how a specific acquisition channel
    would perform given the product, market, and investment level.
    """

    def __init__(
        self,
        agent_id: str,
        profile: ChannelProfile,
        provider: LLMProvider = LLMProvider.ANTHROPIC,
        model: str = None,
    ):
        super().__init__(agent_id, provider, model)
        self.profile = profile
        self.archetype = CHANNEL_ARCHETYPES.get(
            profile.name.lower(),
            {"typical_cac_range": (10, 100), "time_to_results": "medium"}
        )

    @property
    def agent_type(self) -> str:
        return "channel"

    def get_persona_prompt(self) -> str:
        """Define the channel expert persona for the LLM."""
        archetype = self.archetype
        return f"""You are simulating a {self.profile.name} distribution channel in a GTM simulation.

## Channel: {self.profile.name.replace('-', ' ').title()}
- **Priority Level:** {self.profile.priority}/5
- **Budget Allocation:** {self.profile.budget_allocation}%
- **Current Presence:** {self.profile.existing_presence}

## Channel Characteristics
- **Typical CAC Range:** ${archetype.get('typical_cac_range', (10, 100))[0]} - ${archetype.get('typical_cac_range', (10, 100))[1]}
- **Time to Results:** {archetype.get('time_to_results', 'medium')}
- **Scalability:** {archetype.get('scalability', 'medium')}
- **Key Skills Required:** {archetype.get('skill_required', 'various')}

## Strategy Notes
{self.profile.strategy_notes if self.profile.strategy_notes else 'No specific strategy notes.'}

## Your Task
You are an expert in {self.profile.name} distribution. Analyze how this channel would perform
for the given product and market context. Consider:

1. **Reach:** How many potential customers can this channel access?
2. **CAC:** What would customer acquisition cost be for this channel?
3. **Time to Results:** How long until meaningful traction?
4. **Saturation Risk:** When does this channel hit diminishing returns?
5. **Fit:** How well does this channel match the product and ICP?

Be realistic about channel dynamics. Early results often differ from scaled results.
Factor in competition, market timing, and execution quality.

Always respond in valid JSON format."""

    def get_decision_prompt(self, context: Dict[str, Any]) -> str:
        """Build the decision prompt with current simulation context."""
        product = context.get("product", {})
        icp = context.get("icp_personas", [{}])[0] if context.get("icp_personas") else {}
        pricing = context.get("pricing", {})
        cycle = context.get("cycle", 1)
        budget = context.get("budget", 0)
        market_conditions = context.get("market_conditions", {})

        avg_price = 0
        if pricing.get("tiers"):
            prices = [t.get("price", 0) for t in pricing["tiers"]]
            avg_price = sum(prices) / len(prices) if prices else 0

        return f"""## Simulation Cycle {cycle}

## Product Context
**{product.get('name', 'Unknown Product')}**
Category: {product.get('category', 'Unknown')}
Stage: {product.get('stage', 'pre-launch')}

**Value Prop:** {product.get('unique_value_prop', 'Not specified')}

## Target Customer
- **Persona:** {icp.get('name', 'Unknown')}
- **Role:** {icp.get('role', 'Unknown')}
- **Company Size:** {icp.get('company_size', 'Unknown')}
- **Budget Range:** {icp.get('budget_range', 'Unknown')}

## Pricing
- **Model:** {pricing.get('model', 'Unknown')}
- **Average Price Point:** ${avg_price:.0f}/mo

## Your Channel Budget
- **Allocated Budget:** ${budget:,.0f}/month
- **Priority:** {self.profile.priority}/5

## Market Conditions
- **Competition Level:** {market_conditions.get('competition', 'moderate')}
- **Market Maturity:** {market_conditions.get('maturity', 'growing')}
- **Seasonality:** {market_conditions.get('seasonality', 'neutral')}

---

## Channel Performance Projection

Project how the {self.profile.name} channel would perform for this product.

Respond with a JSON object:
```json
{{
    "performance_rating": "poor" | "below_average" | "average" | "good" | "excellent",
    "reasoning": "2-3 sentences explaining channel-product fit",
    "confidence": 0.0-1.0,
    "metrics": {{
        "estimated_cac": <dollars>,
        "monthly_reach": <number of potential customers>,
        "conversion_rate": <percentage as decimal>,
        "time_to_first_results_weeks": <number>,
        "saturation_threshold_users": <number>,
        "roi_multiplier": <X times return on spend>
    }},
    "diminishing_returns": {{
        "threshold_spend": <monthly spend where efficiency drops>,
        "efficiency_after_threshold": <percentage of original efficiency>
    }},
    "risks": ["risk 1", "risk 2"],
    "opportunities": ["opportunity 1", "opportunity 2"],
    "recommended_tactics": ["tactic 1", "tactic 2"],
    "competitive_saturation": 1-10
}}
```"""

    def parse_response(self, response: str) -> AgentResponse:
        """Parse LLM response into structured format."""
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)

            metrics = data.get("metrics", {})
            return AgentResponse(
                decision=data.get("performance_rating", "average"),
                reasoning=data.get("reasoning", ""),
                confidence=float(data.get("confidence", 0.5)),
                metrics={
                    "cac": metrics.get("estimated_cac", 50),
                    "reach": metrics.get("monthly_reach", 1000),
                    "conversion_rate": metrics.get("conversion_rate", 0.02),
                    "time_to_results": metrics.get("time_to_first_results_weeks", 4),
                    "saturation_threshold": metrics.get("saturation_threshold_users", 10000),
                    "roi": metrics.get("roi_multiplier", 1.0),
                    "diminishing_returns": data.get("diminishing_returns", {}),
                    "competitive_saturation": data.get("competitive_saturation", 5),
                },
                signals=[
                    f"risk:{r}" for r in data.get("risks", [])
                ] + [
                    f"opportunity:{o}" for o in data.get("opportunities", [])
                ] + [
                    f"tactic:{t}" for t in data.get("recommended_tactics", [])
                ],
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            return AgentResponse(
                decision="average",
                reasoning=response[:200],
                confidence=0.3,
                metrics={"cac": 50, "reach": 1000, "conversion_rate": 0.02},
                signals=["parse_error"],
            )


def create_channel_agents(
    channels: List[Dict[str, Any]],
    provider: LLMProvider = LLMProvider.ANTHROPIC,
) -> List[ChannelAgent]:
    """
    Create channel agents from config.

    Args:
        channels: List of channel configs from NeoSimConfig
        provider: LLM provider to use

    Returns:
        List of ChannelAgent instances
    """
    agents = []

    for i, ch in enumerate(channels):
        profile = ChannelProfile(
            name=ch.get("name", f"channel_{i}"),
            priority=ch.get("priority", 1),
            budget_allocation=ch.get("budget_allocation", 0),
            existing_presence=ch.get("existing_presence", "none"),
            strategy_notes=ch.get("strategy_notes", ""),
        )

        agent_id = f"channel_{i}"
        agents.append(ChannelAgent(agent_id, profile, provider))

    return agents
