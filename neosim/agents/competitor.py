"""
Competitor Agent

Models competitor countermeasures.
Reacts to user's strategy moves (pricing changes, channel shifts).
Outputs: competitive risk score, predicted counter-moves, vulnerability windows.
"""

import json
import re
from dataclasses import dataclass
from typing import Dict, Any, List
from .base import BaseAgent, AgentResponse, LLMProvider


@dataclass
class CompetitorProfile:
    """Competitor characteristics."""
    name: str
    positioning: str
    pricing: str
    strengths: List[str]
    weaknesses: List[str]
    market_share: str
    aggressiveness: str = "moderate"  # passive, moderate, aggressive


class CompetitorAgent(BaseAgent):
    """
    Competitor Agent - Models competitor reactions.

    Each competitor agent represents a market competitor and
    predicts how they would respond to the user's GTM moves.
    """

    def __init__(
        self,
        agent_id: str,
        profile: CompetitorProfile,
        provider: LLMProvider = LLMProvider.ANTHROPIC,
        model: str = None,
    ):
        super().__init__(agent_id, provider, model)
        self.profile = profile

    @property
    def agent_type(self) -> str:
        return "competitor"

    def get_persona_prompt(self) -> str:
        """Define the competitor persona for the LLM."""
        return f"""You are simulating a competitor company in a GTM simulation.

## You Are: {self.profile.name}
- **Market Position:** {self.profile.positioning}
- **Pricing Strategy:** {self.profile.pricing}
- **Market Share:** {self.profile.market_share}
- **Competitive Style:** {self.profile.aggressiveness}

## Your Strengths
{chr(10).join(f"- {s}" for s in self.profile.strengths)}

## Your Weaknesses
{chr(10).join(f"- {w}" for w in self.profile.weaknesses)}

## Your Task
A new competitor is entering your market with a specific GTM strategy.
Analyze their moves and predict how your company would respond.
Think like a competitive strategy team at {self.profile.name}.

Consider:
- Would you respond at all, or ignore this new entrant?
- If responding, what moves would you make (pricing, features, marketing)?
- What are the vulnerability windows for both sides?
- How does this affect your market position?

Be realistic. Not every new entrant warrants a response.
Big companies often ignore small competitors until they reach meaningful scale.

Always respond in valid JSON format."""

    def get_decision_prompt(self, context: Dict[str, Any]) -> str:
        """Build the decision prompt with current simulation context."""
        new_entrant = context.get("product", {})
        their_pricing = context.get("pricing", {})
        their_channels = context.get("channels", [])
        cycle = context.get("cycle", 1)
        market_signals = context.get("market_signals", {})

        # Build channel strategy info
        channel_info = []
        for ch in their_channels:
            channel_info.append(f"- {ch.get('name', 'Unknown')}: Priority {ch.get('priority', 1)}")

        return f"""## Simulation Cycle {cycle}

## New Market Entrant
**{new_entrant.get('name', 'Unknown Startup')}**

{new_entrant.get('description', 'No description provided.')}

**Their Value Prop:** {new_entrant.get('unique_value_prop', 'Not specified')}

## Their Pricing Strategy
Model: {their_pricing.get('model', 'Unknown')}
Tiers: {', '.join(f"${t.get('price', 0)}/mo" for t in their_pricing.get('tiers', []))}

## Their Channel Strategy
{chr(10).join(channel_info) if channel_info else 'Channels not specified'}

## Current Market Signals
- Market Growth: {market_signals.get('market_growth', 'stable')}
- Customer Churn in Sector: {market_signals.get('sector_churn', 'normal')}
- Their Traction So Far: {market_signals.get('entrant_traction', 'minimal')}

---

## Your Competitive Response

As {self.profile.name}'s strategy team, analyze this new entrant and determine your response.

Respond with a JSON object:
```json
{{
    "response_type": "IGNORE" | "MONITOR" | "COUNTER" | "AGGRESSIVE",
    "reasoning": "2-3 sentences explaining your competitive strategy",
    "confidence": 0.0-1.0,
    "threat_level": 1-10,
    "counter_moves": [
        {{
            "move": "Description of competitive move",
            "timing": "immediate" | "wait_and_see" | "when_they_reach_scale",
            "cost": "low" | "medium" | "high"
        }}
    ],
    "vulnerability_windows": [
        {{
            "description": "When/how the entrant is vulnerable",
            "duration_cycles": <number>,
            "exploitation_difficulty": "easy" | "medium" | "hard"
        }}
    ],
    "market_share_impact": {{
        "short_term": -X to +X percent,
        "long_term": -X to +X percent
    }},
    "their_likely_counter": "What you expect them to do if you respond"
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

            return AgentResponse(
                decision=data.get("response_type", "MONITOR"),
                reasoning=data.get("reasoning", ""),
                confidence=float(data.get("confidence", 0.5)),
                metrics={
                    "threat_level": data.get("threat_level", 5),
                    "market_share_impact": data.get("market_share_impact", {}),
                    "counter_moves_count": len(data.get("counter_moves", [])),
                },
                signals=[
                    f"counter_move:{m.get('move', '')[:50]}"
                    for m in data.get("counter_moves", [])
                ] + [
                    f"vulnerability:{v.get('description', '')[:50]}"
                    for v in data.get("vulnerability_windows", [])
                ],
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            response_type = "MONITOR"
            if "AGGRESSIVE" in response.upper():
                response_type = "AGGRESSIVE"
            elif "COUNTER" in response.upper():
                response_type = "COUNTER"
            elif "IGNORE" in response.upper():
                response_type = "IGNORE"

            return AgentResponse(
                decision=response_type,
                reasoning=response[:200],
                confidence=0.3,
                metrics={"threat_level": 5},
                signals=["parse_error"],
            )


def create_competitor_agents(
    competitors: List[Dict[str, Any]],
    provider: LLMProvider = LLMProvider.ANTHROPIC,
    model: str = None,
) -> List[CompetitorAgent]:
    """
    Create competitor agents from config.

    Args:
        competitors: List of competitor configs from NeoSimConfig
        provider: LLM provider to use
        model: LLM model to use (defaults to provider's default)

    Returns:
        List of CompetitorAgent instances
    """
    agents = []

    for i, comp in enumerate(competitors):
        profile = CompetitorProfile(
            name=comp.get("name", f"Competitor {i}"),
            positioning=comp.get("positioning", "Unknown"),
            pricing=comp.get("pricing", "Unknown"),
            strengths=comp.get("strengths", []),
            weaknesses=comp.get("weaknesses", []),
            market_share=comp.get("market_share", "unknown"),
        )

        agent_id = f"competitor_{i}"
        agents.append(CompetitorAgent(agent_id, profile, provider, model))

    return agents
