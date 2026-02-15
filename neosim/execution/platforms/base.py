"""
Base Platform Generator

Abstract base class for all platform-specific content generators.
Provides shared utilities for content generation.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ContentContext:
    """Shared context for content generation."""
    product_name: str
    product_description: str
    unique_value_prop: str
    category: str
    key_features: List[str]
    pain_points: List[str]
    target_roles: List[str]
    objections: List[Dict[str, str]]  # {theme, counter}
    pricing_model: str
    pricing_tiers: List[Dict[str, Any]]


class BasePlatformGenerator(ABC):
    """
    Abstract base for platform content generators.

    Each platform generator must implement:
    - generate(): Returns platform-specific content
    - Platform constants (char limits, etc.)
    """

    def __init__(self, simulation_result, config):
        """
        Initialize generator with simulation context.

        Args:
            simulation_result: Result from neosim simulation
            config: NeoSimConfig with product/ICP details
        """
        self.result = simulation_result
        self.config = config
        self.context = self._build_context()

    def _build_context(self) -> ContentContext:
        """Extract relevant context from config and results."""
        product = self.config.product
        personas = self.config.icp_personas
        pricing = self.config.pricing

        # Extract pain points from all personas
        pain_points = []
        target_roles = []
        for persona in personas:
            pain_points.extend(persona.pain_points)
            target_roles.append(persona.role)

        # Extract objections from simulation results
        objections = []
        if hasattr(self.result, 'final_metrics'):
            for obj in self.result.final_metrics.objection_clusters[:5]:
                objections.append({
                    "theme": obj.theme,
                    "counter": obj.suggested_counter,
                })

        # Build pricing tiers
        tiers = []
        if pricing and pricing.tiers:
            for tier in pricing.tiers:
                tiers.append({
                    "name": tier.name,
                    "price": tier.price,
                    "features": tier.features,
                })

        return ContentContext(
            product_name=product.name,
            product_description=product.description,
            unique_value_prop=product.unique_value_prop,
            category=product.category,
            key_features=product.key_features or [],
            pain_points=list(set(pain_points)),  # Dedupe
            target_roles=list(set(target_roles)),
            objections=objections,
            pricing_model=pricing.model if pricing else "freemium",
            pricing_tiers=tiers,
        )

    @abstractmethod
    def generate(self) -> Any:
        """Generate platform-specific content."""
        pass

    # =========================================================================
    # Shared Utilities
    # =========================================================================

    def truncate(self, text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to max length with suffix."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)].rstrip() + suffix

    def split_into_chunks(self, text: str, max_length: int) -> List[str]:
        """Split text into chunks respecting word boundaries."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > max_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += word_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def generate_hashtags(self, platform: str, count: int = 5) -> List[str]:
        """Generate relevant hashtags for platform."""
        base_tags = []

        # Category-based tags
        category = self.context.category.lower()
        if category == "saas":
            base_tags.extend(["SaaS", "startup", "software"])
        elif category == "devtool":
            base_tags.extend(["DevTools", "developers", "coding"])
        elif category == "consumer":
            base_tags.extend(["app", "productivity"])

        # Add product-specific
        base_tags.append(self.context.product_name.replace(" ", ""))

        # Platform-specific formatting
        if platform == "twitter":
            return [f"#{tag}" for tag in base_tags[:count]]
        elif platform == "linkedin":
            return [f"#{tag}" for tag in base_tags[:count]]
        elif platform == "instagram":
            return [f"#{tag.lower()}" for tag in base_tags[:count]]

        return base_tags[:count]

    def get_cta(self) -> str:
        """Get appropriate CTA based on pricing model."""
        model = self.context.pricing_model
        if model == "freemium":
            return "Try it free"
        elif model == "free-trial":
            return "Start your free trial"
        elif model == "usage-based":
            return "Get started free"
        return "Learn more"

    def format_feature_list(self, features: List[str], bullet: str = "-") -> str:
        """Format features as bullet list."""
        return "\n".join([f"{bullet} {f}" for f in features])

    def get_pain_point_hook(self) -> str:
        """Get a compelling pain point hook."""
        if self.context.pain_points:
            return f"Tired of {self.context.pain_points[0].lower()}?"
        return f"Struggling with {self.context.category.lower()} challenges?"

    def get_solution_statement(self) -> str:
        """Get solution statement."""
        return f"{self.context.product_name} {self.context.product_description}"

    def get_social_proof_placeholder(self) -> str:
        """Get social proof placeholder text."""
        return "Join [X]+ teams already using {product}".format(
            product=self.context.product_name
        )
