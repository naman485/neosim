"""
Execution Bridge

Converts simulation insights into actionable outputs.
This is where NeoSim goes from "analysis" to "action".

Outputs:
- Landing page copy variants (based on winning messages)
- Ad copy for top channels
- Email sequences
- ICP export for enrichment tools (Clay, Apollo)
- Pitch deck content
- A/B test configurations
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json


@dataclass
class ExecutionPlan:
    """Complete execution plan generated from simulation."""

    # Channel priority
    channel_priority: List[Dict[str, Any]]

    # Copy/messaging
    landing_page_copy: Dict[str, str]
    ad_copy_variants: List[Dict[str, str]]
    email_sequence: List[Dict[str, str]]

    # Objection handling
    objection_responses: Dict[str, str]
    faq_content: List[Dict[str, str]]

    # ICP targeting
    icp_criteria: Dict[str, Any]
    targeting_queries: Dict[str, str]  # For Clay, Apollo, etc.

    # Pricing
    pricing_recommendations: Dict[str, Any]

    # Launch timeline
    launch_phases: List[Dict[str, Any]]


class ExecutionGenerator:
    """
    Generate execution artifacts from simulation results.
    """

    def __init__(self, simulation_result, config):
        self.result = simulation_result
        self.config = config
        self.metrics = simulation_result.final_metrics

    def generate_landing_page_copy(self) -> Dict[str, str]:
        """
        Generate landing page copy based on what resonated with buyers.
        """
        product = self.config.product

        # Extract winning messages from buyer signals
        winning_themes = self._extract_winning_themes()

        return {
            "headline": f"{product.unique_value_prop}",
            "subheadline": f"The {product.category} that {product.description}",
            "cta_primary": "Start Free" if self.config.pricing.model == "freemium" else "Start Trial",
            "cta_secondary": "See Demo",
            "value_props": [
                f"✓ {feature}" for feature in product.key_features[:4]
            ],
            "social_proof_needed": self._get_trust_recommendations(),
            "objection_preempts": self._get_objection_preempts(),
        }

    def generate_ad_copy(self) -> List[Dict[str, str]]:
        """
        Generate ad copy variants for top channels.
        """
        variants = []
        top_channels = self.metrics.channel_rankings[:3]

        for channel in top_channels:
            if channel.channel in ["paid-ads", "organic-social"]:
                variants.append({
                    "channel": channel.channel,
                    "headline": f"{self.config.product.unique_value_prop}",
                    "body": self._generate_ad_body(channel.channel),
                    "cta": self._get_channel_cta(channel.channel),
                })

        return variants

    def generate_email_sequence(self) -> List[Dict[str, str]]:
        """
        Generate email sequence based on objections and buyer journey.
        """
        objections = self.metrics.objection_clusters

        sequence = [
            {
                "day": 0,
                "subject": f"Welcome to {self.config.product.name}",
                "purpose": "Activation - get them to first value",
                "key_message": "Here's how to get started in 2 minutes",
            },
            {
                "day": 2,
                "subject": "Quick tip to get more from {product}",
                "purpose": "Education - show key feature",
                "key_message": "Most users miss this powerful feature",
            },
            {
                "day": 5,
                "subject": "How {similar_company} uses {product}",
                "purpose": "Social proof - address trust objection",
                "key_message": "Case study showing concrete results",
            },
        ]

        # Add objection-specific emails
        for obj in objections[:2]:
            sequence.append({
                "day": 7 + objections.index(obj) * 3,
                "subject": f"About {obj.theme.lower()}...",
                "purpose": f"Address {obj.theme} objection",
                "key_message": obj.suggested_counter,
            })

        return sequence

    def generate_icp_export(self) -> Dict[str, Any]:
        """
        Generate ICP criteria for enrichment tools (Clay, Apollo, etc.).
        """
        personas = self.config.icp_personas

        if not personas:
            return {}

        primary_icp = personas[0]

        return {
            "clay_filters": {
                "job_titles": [primary_icp.role],
                "company_size": self._size_to_range(primary_icp.company_size),
                "industries": [self.config.product.category],
                "keywords": primary_icp.pain_points[:3],
            },
            "apollo_query": self._build_apollo_query(primary_icp),
            "linkedin_search": self._build_linkedin_query(primary_icp),
            "exclusions": [
                "Competitors",
                "Agencies",
                "Students",
            ],
        }

    def generate_launch_plan(self) -> List[Dict[str, Any]]:
        """
        Generate phased launch plan based on simulation results.
        """
        top_channels = self.metrics.channel_rankings

        phases = [
            {
                "phase": "Soft Launch (Week 1-2)",
                "goal": "Validate core value prop with design partners",
                "channels": ["product-led", "community"],
                "metrics_to_track": ["activation_rate", "time_to_value"],
                "success_criteria": "10 active users, 3 testimonials",
            },
            {
                "phase": "Community Launch (Week 3-4)",
                "goal": "Build word-of-mouth momentum",
                "channels": [c.channel for c in top_channels if c.channel in ["community", "organic-social"]][:2],
                "metrics_to_track": ["organic_signups", "referral_rate"],
                "success_criteria": "100 users, 20% organic growth",
            },
            {
                "phase": "Scale Launch (Week 5-8)",
                "goal": "Accelerate with paid channels if economics work",
                "channels": [c.channel for c in top_channels[:2]],
                "metrics_to_track": ["cac", "conversion_rate", "ltv"],
                "success_criteria": f"CAC < ${self.metrics.cac.mid:.0f}, Conv > {self.metrics.conversion_rate.mid:.1%}",
            },
        ]

        return phases

    def generate_full_plan(self) -> ExecutionPlan:
        """Generate complete execution plan."""
        return ExecutionPlan(
            channel_priority=[
                {"channel": c.channel, "score": c.score, "cac": c.cac.mid}
                for c in self.metrics.channel_rankings
            ],
            landing_page_copy=self.generate_landing_page_copy(),
            ad_copy_variants=self.generate_ad_copy(),
            email_sequence=self.generate_email_sequence(),
            objection_responses={
                obj.theme: obj.suggested_counter
                for obj in self.metrics.objection_clusters
            },
            faq_content=self._generate_faq(),
            icp_criteria=self.generate_icp_export(),
            pricing_recommendations=self._get_pricing_recommendations(),
            launch_phases=self.generate_launch_plan(),
        )

    def export_to_json(self, path: str) -> None:
        """Export execution plan to JSON."""
        plan = self.generate_full_plan()
        with open(path, 'w') as f:
            json.dump({
                "channel_priority": plan.channel_priority,
                "landing_page_copy": plan.landing_page_copy,
                "ad_copy_variants": plan.ad_copy_variants,
                "email_sequence": plan.email_sequence,
                "objection_responses": plan.objection_responses,
                "icp_criteria": plan.icp_criteria,
                "launch_phases": plan.launch_phases,
            }, f, indent=2)

    # Helper methods
    def _extract_winning_themes(self) -> List[str]:
        return [obj.theme for obj in self.metrics.objection_clusters]

    def _get_trust_recommendations(self) -> List[str]:
        trust_objections = [
            obj for obj in self.metrics.objection_clusters
            if "trust" in obj.theme.lower()
        ]
        if trust_objections:
            return ["Add customer logos", "Show testimonials", "Display security badges"]
        return ["Add social proof section"]

    def _get_objection_preempts(self) -> List[str]:
        return [
            f"Addresses {obj.theme}: {obj.suggested_counter}"
            for obj in self.metrics.objection_clusters[:3]
        ]

    def _generate_ad_body(self, channel: str) -> str:
        product = self.config.product
        if channel == "paid-ads":
            return f"Stop wasting time on {self.config.icp_personas[0].pain_points[0] if self.config.icp_personas else 'manual work'}. {product.name} helps you {product.unique_value_prop}."
        return f"{product.unique_value_prop}. Join thousands of {self.config.icp_personas[0].role if self.config.icp_personas else 'users'}s."

    def _get_channel_cta(self, channel: str) -> str:
        if self.config.pricing.model == "freemium":
            return "Try Free"
        elif self.config.pricing.model == "free-trial":
            return "Start Free Trial"
        return "Get Started"

    def _size_to_range(self, size: str) -> str:
        mapping = {
            "solo": "1-1",
            "startup": "2-50",
            "smb": "51-200",
            "enterprise": "201-10000",
        }
        return mapping.get(size, "2-50")

    def _build_apollo_query(self, icp) -> str:
        return f"title:{icp.role} AND company_size:{self._size_to_range(icp.company_size)}"

    def _build_linkedin_query(self, icp) -> str:
        return f'"{icp.role}" AND "{icp.company_size}"'

    def _generate_faq(self) -> List[Dict[str, str]]:
        return [
            {"q": f"What is {self.config.product.name}?", "a": self.config.product.description},
            {"q": "How much does it cost?", "a": f"Starting at ${self.config.pricing.tiers[0].price}/mo" if self.config.pricing.tiers else "Contact us"},
        ]

    def _get_pricing_recommendations(self) -> Dict[str, Any]:
        return {
            "model": self.config.pricing.model,
            "recommendation": "Consider anchoring with higher tier to make mid-tier attractive",
            "psychological_threshold": self._get_price_threshold(),
        }

    def _get_price_threshold(self) -> str:
        if not self.config.pricing.tiers:
            return "unknown"
        max_price = max(t.price for t in self.config.pricing.tiers)
        if max_price <= 10:
            return "impulse"
        elif max_price <= 50:
            return "considered"
        elif max_price <= 200:
            return "evaluated"
        return "enterprise"
