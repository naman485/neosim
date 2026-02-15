"""
Market Data Layer

Provides real market benchmarks and constraints for simulation grounding.
Without this, agents hallucinate plausible-but-wrong numbers.

Data sources:
- Industry benchmarks (public data from OpenView, Bessemer, etc.)
- Category-specific conversion rates
- Channel-specific CAC ranges
- Pricing psychology research
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class MarketBenchmarks:
    """Industry benchmarks by category."""

    # CAC benchmarks by category (USD)
    CAC_RANGES = {
        "SaaS": {"low": 50, "mid": 200, "high": 500},
        "DevTool": {"low": 20, "mid": 100, "high": 300},
        "Consumer": {"low": 5, "mid": 30, "high": 100},
        "Marketplace": {"low": 30, "mid": 150, "high": 400},
        "API": {"low": 100, "mid": 300, "high": 800},
        "Enterprise": {"low": 500, "mid": 2000, "high": 10000},
    }

    # Conversion rate benchmarks (visitor to signup)
    CONVERSION_RATES = {
        "SaaS": {"low": 0.01, "mid": 0.03, "high": 0.07},
        "DevTool": {"low": 0.02, "mid": 0.05, "high": 0.10},
        "Consumer": {"low": 0.005, "mid": 0.02, "high": 0.05},
        "freemium": {"low": 0.02, "mid": 0.05, "high": 0.10},  # Free to paid
        "free-trial": {"low": 0.10, "mid": 0.20, "high": 0.40},
        "paid-only": {"low": 0.01, "mid": 0.02, "high": 0.05},
    }

    # Channel performance by category
    CHANNEL_EFFECTIVENESS = {
        "SaaS": {
            "organic-social": 0.6,
            "paid-ads": 0.7,
            "community": 0.5,
            "outbound": 0.8,
            "seo": 0.7,
            "partnerships": 0.6,
            "product-led": 0.8,
        },
        "DevTool": {
            "organic-social": 0.8,  # Twitter/X strong for devs
            "paid-ads": 0.3,  # Devs hate ads
            "community": 0.9,  # Discord, GitHub strong
            "outbound": 0.2,  # Don't cold email devs
            "seo": 0.7,
            "partnerships": 0.6,
            "product-led": 0.95,  # Best channel for devtools
        },
        "Consumer": {
            "organic-social": 0.8,
            "paid-ads": 0.9,
            "community": 0.5,
            "outbound": 0.1,
            "seo": 0.6,
            "partnerships": 0.7,
            "product-led": 0.7,
        },
    }

    # Pricing psychology thresholds
    PRICE_THRESHOLDS = {
        "impulse": 10,  # No thought needed
        "considered": 50,  # Some evaluation
        "evaluated": 200,  # Requires demo/trial
        "enterprise": 1000,  # Requires sales process
    }

    # Time to results by channel (weeks)
    CHANNEL_TIME_TO_RESULTS = {
        "paid-ads": 2,
        "outbound": 4,
        "organic-social": 8,
        "community": 12,
        "seo": 16,
        "partnerships": 12,
        "product-led": 4,
    }


def get_category_benchmarks(category: str) -> Dict:
    """Get all benchmarks for a category."""
    benchmarks = MarketBenchmarks()
    return {
        "cac": benchmarks.CAC_RANGES.get(category, benchmarks.CAC_RANGES["SaaS"]),
        "conversion": benchmarks.CONVERSION_RATES.get(
            category, benchmarks.CONVERSION_RATES["SaaS"]
        ),
        "channel_effectiveness": benchmarks.CHANNEL_EFFECTIVENESS.get(
            category, benchmarks.CHANNEL_EFFECTIVENESS["SaaS"]
        ),
    }


def get_pricing_model_benchmarks(model: str) -> Dict:
    """Get conversion benchmarks by pricing model."""
    benchmarks = MarketBenchmarks()
    return benchmarks.CONVERSION_RATES.get(model, {"low": 0.02, "mid": 0.05, "high": 0.10})


def get_channel_benchmarks(channel: str, category: str = "SaaS") -> Dict:
    """Get benchmarks for a specific channel."""
    benchmarks = MarketBenchmarks()
    effectiveness = benchmarks.CHANNEL_EFFECTIVENESS.get(
        category, benchmarks.CHANNEL_EFFECTIVENESS["SaaS"]
    ).get(channel, 0.5)

    time_to_results = benchmarks.CHANNEL_TIME_TO_RESULTS.get(channel, 8)

    return {
        "effectiveness": effectiveness,
        "time_to_results_weeks": time_to_results,
        "recommended": effectiveness > 0.6,
    }


def constrain_prediction(
    predicted_value: float,
    metric_type: str,
    category: str,
    confidence: float = 0.5,
) -> Dict:
    """
    Constrain a prediction to realistic ranges.

    This prevents the LLM from hallucinating numbers that are
    way outside industry norms. The prediction is blended with
    benchmarks based on confidence level.
    """
    benchmarks = MarketBenchmarks()

    if metric_type == "cac":
        bench = benchmarks.CAC_RANGES.get(category, benchmarks.CAC_RANGES["SaaS"])
    elif metric_type == "conversion":
        bench = benchmarks.CONVERSION_RATES.get(category, benchmarks.CONVERSION_RATES["SaaS"])
    else:
        return {"value": predicted_value, "constrained": False}

    # Blend prediction with benchmark based on confidence
    # Low confidence = lean more on benchmarks
    # High confidence = trust prediction more
    blend_factor = confidence

    constrained = (
        predicted_value * blend_factor + bench["mid"] * (1 - blend_factor)
    )

    # Hard constraints - never go outside reasonable bounds
    constrained = max(bench["low"] * 0.5, min(bench["high"] * 2, constrained))

    return {
        "value": constrained,
        "original": predicted_value,
        "benchmark_mid": bench["mid"],
        "constrained": abs(constrained - predicted_value) > 0.01,
    }


# User calibration - let users input known data points
class UserCalibration:
    """
    Let users input known data points to calibrate the simulation.

    Example: "I know from beta that my conversion is ~5%"
    This adjusts agent behavior to be anchored on user's reality.
    """

    def __init__(self):
        self.data_points: Dict[str, float] = {}

    def set(self, metric: str, value: float, confidence: float = 0.8):
        """Set a known data point."""
        self.data_points[metric] = {
            "value": value,
            "confidence": confidence,
        }

    def get(self, metric: str) -> Optional[Dict]:
        """Get a user-provided data point."""
        return self.data_points.get(metric)

    def has(self, metric: str) -> bool:
        """Check if user has provided this metric."""
        return metric in self.data_points

    def to_prompt_context(self) -> str:
        """Convert to context string for agent prompts."""
        if not self.data_points:
            return ""

        lines = ["## Known Data Points (from user)"]
        for metric, data in self.data_points.items():
            lines.append(f"- {metric}: {data['value']} (confidence: {data['confidence']:.0%})")
        lines.append("\nUse these as anchors for your predictions.")
        return "\n".join(lines)
