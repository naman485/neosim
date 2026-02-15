"""
Buyer Agent

Simulates ICP personas responding to positioning.
Reacts to pitches with buy/pass/object decisions.
Outputs: conversion signals, objection themes, willingness-to-pay ranges.
"""

import json
import re
from dataclasses import dataclass
from typing import Dict, Any, List
from .base import BaseAgent, AgentResponse, LLMProvider


@dataclass
class BuyerPersona:
    """Specific buyer persona characteristics."""
    name: str
    role: str
    company_size: str
    pain_points: List[str]
    goals: List[str]
    budget_range: str
    decision_speed: str
    objection_tendencies: List[str]


class BuyerAgent(BaseAgent):
    """
    Buyer Agent - Simulates potential customers.

    Each buyer agent represents an ICP persona and makes
    buy/pass/object decisions based on the product positioning,
    pricing, and their persona characteristics.
    """

    def __init__(
        self,
        agent_id: str,
        persona: BuyerPersona,
        provider: LLMProvider = LLMProvider.ANTHROPIC,
        model: str = None,
    ):
        super().__init__(agent_id, provider, model)
        self.persona = persona

    @property
    def agent_type(self) -> str:
        return "buyer"

    def get_persona_prompt(self) -> str:
        """Define the buyer persona for the LLM."""
        return f"""You are simulating a potential buyer in a GTM simulation.

## Your Persona: {self.persona.name}
- **Role:** {self.persona.role}
- **Company Size:** {self.persona.company_size}
- **Budget Range:** {self.persona.budget_range}
- **Decision Speed:** {self.persona.decision_speed}

## Your Pain Points
{chr(10).join(f"- {p}" for p in self.persona.pain_points)}

## Your Goals
{chr(10).join(f"- {g}" for g in self.persona.goals)}

## Your Typical Objections
{chr(10).join(f"- {o}" for o in self.persona.objection_tendencies)}

## Your Task
You will be presented with a product pitch. Evaluate it from your persona's perspective.
Make a realistic decision about whether you would:
- **BUY**: This solves my problem at an acceptable price
- **PASS**: Not interested, doesn't fit my needs
- **OBJECT**: Interested but have concerns that need addressing

Be realistic and critical. Not every product is right for every buyer.
Your responses should reflect genuine buyer behavior, including skepticism.

Always respond in valid JSON format."""

    def get_decision_prompt(self, context: Dict[str, Any]) -> str:
        """Build the decision prompt with current simulation context."""
        product = context.get("product", {})
        pricing = context.get("pricing", {})
        cycle = context.get("cycle", 1)
        pitch = context.get("pitch", "")

        # Build pricing info
        pricing_info = []
        for tier in pricing.get("tiers", []):
            pricing_info.append(f"- {tier['name']}: ${tier['price']}/mo")

        return f"""## Simulation Cycle {cycle}

## Product Being Pitched
**{product.get('name', 'Unknown Product')}**

{product.get('description', 'No description provided.')}

**Unique Value Prop:** {product.get('unique_value_prop', 'Not specified')}

**Key Features:**
{chr(10).join(f"- {f}" for f in product.get('key_features', ['Not specified']))}

## Pricing
Model: {pricing.get('model', 'Not specified')}
{chr(10).join(pricing_info) if pricing_info else 'Pricing not specified'}

## The Pitch
{pitch if pitch else 'Standard product pitch based on the description above.'}

---

## Your Decision

Evaluate this product from your persona's perspective. Consider:
1. Does this solve your pain points?
2. Is the pricing acceptable for your budget?
3. Does the value proposition resonate with your goals?
4. What objections do you have?

Respond with a JSON object:
```json
{{
    "decision": "BUY" | "PASS" | "OBJECT",
    "reasoning": "2-3 sentences explaining your decision from your persona's perspective",
    "confidence": 0.0-1.0,
    "willingness_to_pay": {{
        "min": <number>,
        "max": <number>,
        "ideal": <number>
    }},
    "objections": ["objection 1", "objection 2"],
    "what_would_change_mind": "What would make you reconsider if you passed/objected",
    "perceived_value_score": 1-10
}}
```"""

    def parse_response(self, response: str) -> AgentResponse:
        """Parse LLM response into structured format."""
        # Try to extract JSON from response
        try:
            # Find JSON block in response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)

            return AgentResponse(
                decision=data.get("decision", "PASS"),
                reasoning=data.get("reasoning", ""),
                confidence=float(data.get("confidence", 0.5)),
                metrics={
                    "willingness_to_pay": data.get("willingness_to_pay", {}),
                    "perceived_value_score": data.get("perceived_value_score", 5),
                },
                signals=[
                    f"objection:{obj}" for obj in data.get("objections", [])
                ] + [f"change_mind:{data.get('what_would_change_mind', '')}"],
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # Fallback parsing
            decision = "PASS"
            if "BUY" in response.upper():
                decision = "BUY"
            elif "OBJECT" in response.upper():
                decision = "OBJECT"

            return AgentResponse(
                decision=decision,
                reasoning=response[:200],
                confidence=0.3,
                metrics={},
                signals=["parse_error"],
            )


def create_buyer_agents(
    personas: List[Dict[str, Any]],
    count_per_persona: int = 5,
    provider: LLMProvider = LLMProvider.ANTHROPIC,
) -> List[BuyerAgent]:
    """
    Create multiple buyer agents from persona definitions.

    Args:
        personas: List of persona configs from NeoSimConfig
        count_per_persona: How many agents per persona type
        provider: LLM provider to use

    Returns:
        List of BuyerAgent instances
    """
    agents = []
    agent_num = 0

    for persona_config in personas:
        persona = BuyerPersona(
            name=persona_config.get("name", f"Persona {agent_num}"),
            role=persona_config.get("role", "Unknown"),
            company_size=persona_config.get("company_size", "startup"),
            pain_points=persona_config.get("pain_points", []),
            goals=persona_config.get("goals", []),
            budget_range=persona_config.get("budget_range", "unknown"),
            decision_speed=persona_config.get("decision_speed", "medium"),
            objection_tendencies=persona_config.get("objection_tendencies", []),
        )

        for i in range(count_per_persona):
            agent_id = f"buyer_{agent_num}"
            agents.append(BuyerAgent(agent_id, persona, provider))
            agent_num += 1

    return agents
