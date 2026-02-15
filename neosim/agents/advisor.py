"""
Advisor Agent

Synthesizes and challenges the outputs from all other agents.
Reviews all agent outputs, identifies blind spots, suggests pivots, flags overconfidence.
Outputs: strategic recommendations, risk flags, confidence intervals on all metrics.
"""

import json
import re
from typing import Dict, Any, List
from .base import BaseAgent, AgentResponse, LLMProvider


class AdvisorAgent(BaseAgent):
    """
    Advisor Agent - The strategic synthesizer.

    This agent reviews outputs from all other agents and provides:
    - Overall strategic assessment
    - Identification of blind spots
    - Confidence intervals on key metrics
    - Recommendations for strategy pivots
    - Risk flags and warnings
    """

    def __init__(
        self,
        agent_id: str = "advisor_0",
        provider: LLMProvider = LLMProvider.ANTHROPIC,
        model: str = None,
    ):
        super().__init__(agent_id, provider, model, temperature=0.5)  # Lower temp for analysis

    @property
    def agent_type(self) -> str:
        return "advisor"

    def get_persona_prompt(self) -> str:
        """Define the advisor persona for the LLM."""
        return """You are a world-class GTM strategist and startup advisor in a simulation.

## Your Role
You are the strategic advisor who synthesizes insights from:
- **Buyer Agents:** Simulated customer reactions and objections
- **Competitor Agents:** Competitive threat analysis and counter-moves
- **Channel Agents:** Distribution channel performance projections

Your job is NOT to be optimistic or encouraging. Your job is to:
1. **Synthesize:** Combine all agent outputs into coherent strategic insight
2. **Challenge:** Identify blind spots, overconfidence, and weak assumptions
3. **Quantify:** Provide confidence intervals on key metrics
4. **Recommend:** Suggest concrete strategy pivots based on the data

## Your Perspective
Think like a combination of:
- A seasoned VC who's seen 1000 pitches and knows the failure modes
- A growth advisor who's scaled multiple companies
- A skeptical board member who asks hard questions

Be direct. Founders need honesty, not encouragement.
Flag risks clearly. Quantify uncertainty.

Always respond in valid JSON format."""

    def get_decision_prompt(self, context: Dict[str, Any]) -> str:
        """Build the decision prompt with all agent outputs."""
        product = context.get("product", {})
        pricing = context.get("pricing", {})
        cycle = context.get("cycle", 1)

        # Agent outputs from current cycle
        buyer_results = context.get("buyer_results", [])
        competitor_results = context.get("competitor_results", [])
        channel_results = context.get("channel_results", [])

        # Aggregate buyer data
        buyer_summary = self._summarize_buyer_results(buyer_results)
        competitor_summary = self._summarize_competitor_results(competitor_results)
        channel_summary = self._summarize_channel_results(channel_results)

        return f"""## Simulation Cycle {cycle} - Strategic Synthesis

## Product
**{product.get('name', 'Unknown')}**: {product.get('description', 'N/A')[:200]}

## Pricing Model
{pricing.get('model', 'Unknown')} - Tiers: {', '.join(f"${t.get('price', 0)}" for t in pricing.get('tiers', []))}

---

## Buyer Agent Results (n={len(buyer_results)})
{buyer_summary}

## Competitor Agent Results (n={len(competitor_results)})
{competitor_summary}

## Channel Agent Results (n={len(channel_results)})
{channel_summary}

---

## Your Strategic Synthesis

Analyze all agent outputs and provide your assessment.

Respond with a JSON object:
```json
{{
    "overall_assessment": "strong" | "promising" | "uncertain" | "concerning" | "weak",
    "reasoning": "3-4 sentences synthesizing the key findings",
    "confidence_score": 0.0-1.0,

    "key_metrics": {{
        "projected_cac": {{
            "low": <number>,
            "mid": <number>,
            "high": <number>,
            "confidence": "high" | "medium" | "low"
        }},
        "projected_conversion_rate": {{
            "low": <decimal>,
            "mid": <decimal>,
            "high": <decimal>,
            "confidence": "high" | "medium" | "low"
        }},
        "time_to_pmf_months": {{
            "low": <number>,
            "mid": <number>,
            "high": <number>,
            "confidence": "high" | "medium" | "low"
        }},
        "competitive_moat_strength": 1-10
    }},

    "blind_spots": [
        "Critical assumption or risk that isn't being addressed"
    ],

    "overconfidence_flags": [
        "Area where the strategy seems overconfident"
    ],

    "top_objections": [
        {{
            "objection": "The objection",
            "frequency": "how often it appeared",
            "suggested_counter": "how to address it"
        }}
    ],

    "channel_ranking": [
        {{
            "channel": "channel name",
            "score": 1-10,
            "rationale": "why this ranking"
        }}
    ],

    "strategic_recommendations": [
        {{
            "action": "What to do",
            "priority": "critical" | "high" | "medium" | "low",
            "rationale": "Why this matters"
        }}
    ],

    "biggest_risk": "The single biggest risk to this GTM strategy",
    "biggest_opportunity": "The single biggest opportunity being underexploited"
}}
```"""

    def _summarize_buyer_results(self, results: List[Dict]) -> str:
        """Summarize buyer agent results."""
        if not results:
            return "No buyer agent data available."

        buy_count = sum(1 for r in results if r.get("decision") == "BUY")
        pass_count = sum(1 for r in results if r.get("decision") == "PASS")
        object_count = sum(1 for r in results if r.get("decision") == "OBJECT")

        # Collect objections
        objections = []
        for r in results:
            for signal in r.get("signals", []):
                if signal.startswith("objection:"):
                    objections.append(signal.replace("objection:", ""))

        return f"""- **Decisions:** {buy_count} BUY, {object_count} OBJECT, {pass_count} PASS
- **Conversion Rate:** {buy_count / len(results) * 100:.1f}%
- **Top Objections:** {', '.join(objections[:5]) if objections else 'None captured'}
- **Average Confidence:** {sum(r.get('confidence', 0.5) for r in results) / len(results):.2f}"""

    def _summarize_competitor_results(self, results: List[Dict]) -> str:
        """Summarize competitor agent results."""
        if not results:
            return "No competitor agent data available."

        responses = {}
        threat_levels = []
        for r in results:
            resp = r.get("decision", "MONITOR")
            responses[resp] = responses.get(resp, 0) + 1
            threat_levels.append(r.get("metrics", {}).get("threat_level", 5))

        avg_threat = sum(threat_levels) / len(threat_levels) if threat_levels else 5

        return f"""- **Response Types:** {', '.join(f'{k}: {v}' for k, v in responses.items())}
- **Average Threat Level:** {avg_threat:.1f}/10
- **Counter-Moves Expected:** {'Yes' if any(r.get('decision') in ['COUNTER', 'AGGRESSIVE'] for r in results) else 'No'}"""

    def _summarize_channel_results(self, results: List[Dict]) -> str:
        """Summarize channel agent results."""
        if not results:
            return "No channel agent data available."

        summaries = []
        for r in results:
            metrics = r.get("metrics", {})
            summaries.append(
                f"- **{r.get('channel', 'Unknown')}:** {r.get('decision', 'N/A')} "
                f"(CAC: ${metrics.get('cac', 'N/A')}, ROI: {metrics.get('roi', 'N/A')}x)"
            )

        return "\n".join(summaries) if summaries else "No channel data."

    def parse_response(self, response: str) -> AgentResponse:
        """Parse LLM response into structured format."""
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(response)

            return AgentResponse(
                decision=data.get("overall_assessment", "uncertain"),
                reasoning=data.get("reasoning", ""),
                confidence=float(data.get("confidence_score", 0.5)),
                metrics={
                    "key_metrics": data.get("key_metrics", {}),
                    "channel_ranking": data.get("channel_ranking", []),
                    "competitive_moat": data.get("key_metrics", {}).get("competitive_moat_strength", 5),
                },
                signals=(
                    [f"blind_spot:{b}" for b in data.get("blind_spots", [])] +
                    [f"overconfidence:{o}" for o in data.get("overconfidence_flags", [])] +
                    [f"recommendation:{r.get('action', '')}" for r in data.get("strategic_recommendations", [])] +
                    [f"risk:{data.get('biggest_risk', '')}"] +
                    [f"opportunity:{data.get('biggest_opportunity', '')}"]
                ),
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            return AgentResponse(
                decision="uncertain",
                reasoning=response[:300],
                confidence=0.3,
                metrics={},
                signals=["parse_error"],
            )

    def synthesize(
        self,
        context: Dict[str, Any],
        buyer_results: List[AgentResponse],
        competitor_results: List[AgentResponse],
        channel_results: List[AgentResponse],
    ) -> AgentResponse:
        """
        Synthesize all agent results into strategic assessment.

        This is the main entry point for the advisor agent.

        Args:
            context: Base simulation context
            buyer_results: Results from all buyer agents
            competitor_results: Results from all competitor agents
            channel_results: Results from all channel agents

        Returns:
            Strategic synthesis as AgentResponse
        """
        # Convert AgentResponses to dicts for the prompt
        full_context = {
            **context,
            "buyer_results": [
                {"decision": r.decision, "confidence": r.confidence,
                 "metrics": r.metrics, "signals": r.signals}
                for r in buyer_results
            ],
            "competitor_results": [
                {"decision": r.decision, "confidence": r.confidence,
                 "metrics": r.metrics, "signals": r.signals}
                for r in competitor_results
            ],
            "channel_results": [
                {"decision": r.decision, "confidence": r.confidence,
                 "metrics": r.metrics, "signals": r.signals,
                 "channel": context.get("channels", [{}])[i].get("name", f"channel_{i}")
                 if i < len(context.get("channels", [])) else f"channel_{i}"}
                for i, r in enumerate(channel_results)
            ],
        }

        return self.decide(full_context)
