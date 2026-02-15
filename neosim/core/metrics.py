"""
Metrics Aggregator

Computes and tracks simulation metrics across cycles.
Produces confidence intervals and final projections.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import statistics


@dataclass
class ConfidenceInterval:
    """A metric with confidence bounds."""
    low: float
    mid: float
    high: float
    confidence: str  # high, medium, low

    def to_dict(self) -> Dict[str, Any]:
        return {
            "low": self.low,
            "mid": self.mid,
            "high": self.high,
            "confidence": self.confidence,
        }


@dataclass
class ObjectionCluster:
    """Clustered objections with frequency."""
    theme: str
    count: int
    examples: List[str]
    suggested_counter: str = ""


@dataclass
class ChannelRanking:
    """Channel performance ranking."""
    channel: str
    score: float
    cac: ConfidenceInterval
    roi: float
    reach: int
    rationale: str


@dataclass
class SimulationMetrics:
    """Complete metrics output from a simulation."""
    # Core projected metrics
    cac: ConfidenceInterval
    conversion_rate: ConfidenceInterval
    ltv: ConfidenceInterval
    time_to_breakeven_months: ConfidenceInterval

    # Strategic metrics
    competitive_threat_score: float
    market_readiness_score: float
    overall_confidence: float

    # Detailed breakdowns
    objection_clusters: List[ObjectionCluster]
    channel_rankings: List[ChannelRanking]

    # Raw data
    cycle_metrics: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "cac": self.cac.to_dict(),
            "conversion_rate": self.conversion_rate.to_dict(),
            "ltv": self.ltv.to_dict(),
            "time_to_breakeven_months": self.time_to_breakeven_months.to_dict(),
            "competitive_threat_score": self.competitive_threat_score,
            "market_readiness_score": self.market_readiness_score,
            "overall_confidence": self.overall_confidence,
            "objection_clusters": [
                {
                    "theme": o.theme,
                    "count": o.count,
                    "examples": o.examples[:3],
                    "suggested_counter": o.suggested_counter,
                }
                for o in self.objection_clusters
            ],
            "channel_rankings": [
                {
                    "channel": c.channel,
                    "score": c.score,
                    "cac": c.cac.to_dict(),
                    "roi": c.roi,
                    "reach": c.reach,
                    "rationale": c.rationale,
                }
                for c in self.channel_rankings
            ],
        }


class MetricsAggregator:
    """
    Aggregates metrics across simulation cycles.

    Tracks running statistics and computes final metrics
    with confidence intervals.
    """

    def __init__(self):
        self.cycle_metrics: List[Dict[str, Any]] = []
        self.all_objections: List[str] = []
        self.channel_data: Dict[str, List[Dict]] = {}

    def add_cycle(self, cycle_result) -> None:
        """
        Add cycle results to aggregation.

        Args:
            cycle_result: CycleResult from simulation
        """
        # Store cycle metrics
        self.cycle_metrics.append(cycle_result.metrics)

        # Extract objections from buyer responses
        for response in cycle_result.buyer_responses:
            for signal in response.signals:
                if signal.startswith("objection:"):
                    self.all_objections.append(signal.replace("objection:", ""))

        # Aggregate channel data
        for i, response in enumerate(cycle_result.channel_responses):
            channel_name = f"channel_{i}"  # Will be mapped to actual names later
            if channel_name not in self.channel_data:
                self.channel_data[channel_name] = []
            self.channel_data[channel_name].append({
                "cac": response.metrics.get("cac", 50),
                "roi": response.metrics.get("roi", 1.0),
                "reach": response.metrics.get("reach", 1000),
                "rating": response.decision,
            })

    def compute_final_metrics(self) -> SimulationMetrics:
        """
        Compute final simulation metrics.

        Returns:
            SimulationMetrics with all projections and confidence intervals
        """
        if not self.cycle_metrics:
            return self._empty_metrics()

        # Compute CAC confidence interval
        cac_values = [m.get("avg_cac", 50) for m in self.cycle_metrics]
        cac = self._compute_ci(cac_values, "cac")

        # Compute conversion rate CI
        conv_values = [m.get("conversion_rate", 0.05) for m in self.cycle_metrics]
        conversion_rate = self._compute_ci(conv_values, "rate")

        # Estimate LTV (simplified: assume 12-month average retention)
        # LTV = ARPU * months * conversion
        avg_conv = statistics.mean(conv_values) if conv_values else 0.05
        ltv = ConfidenceInterval(
            low=avg_conv * 100 * 6,  # 6 months, $100 ARPU
            mid=avg_conv * 100 * 12,  # 12 months
            high=avg_conv * 100 * 24,  # 24 months
            confidence="low",  # LTV is always uncertain pre-launch
        )

        # Time to breakeven
        avg_cac = statistics.mean(cac_values) if cac_values else 50
        monthly_value = 50  # Assumed average plan price
        months_to_break = avg_cac / monthly_value if monthly_value > 0 else 12
        time_to_breakeven = ConfidenceInterval(
            low=max(1, months_to_break * 0.5),
            mid=months_to_break,
            high=months_to_break * 2,
            confidence="medium",
        )

        # Competitive threat
        threat_values = [m.get("avg_competitor_threat", 5) for m in self.cycle_metrics]
        competitive_threat = statistics.mean(threat_values) if threat_values else 5.0

        # Market readiness (based on conversion and confidence)
        confidence_values = [m.get("avg_buyer_confidence", 0.5) for m in self.cycle_metrics]
        avg_confidence = statistics.mean(confidence_values) if confidence_values else 0.5
        market_readiness = (avg_conv * 10 + avg_confidence * 10) / 2

        # Cluster objections
        objection_clusters = self._cluster_objections()

        # Rank channels
        channel_rankings = self._rank_channels()

        # Overall confidence
        overall_confidence = self._compute_overall_confidence()

        return SimulationMetrics(
            cac=cac,
            conversion_rate=conversion_rate,
            ltv=ltv,
            time_to_breakeven_months=time_to_breakeven,
            competitive_threat_score=competitive_threat,
            market_readiness_score=market_readiness,
            overall_confidence=overall_confidence,
            objection_clusters=objection_clusters,
            channel_rankings=channel_rankings,
            cycle_metrics=self.cycle_metrics,
        )

    def _compute_ci(self, values: List[float], metric_type: str) -> ConfidenceInterval:
        """Compute confidence interval for a metric."""
        if not values:
            return ConfidenceInterval(0, 0, 0, "low")

        mean = statistics.mean(values)
        if len(values) > 1:
            stdev = statistics.stdev(values)
        else:
            stdev = mean * 0.2  # Assume 20% variance if single value

        # Confidence based on variance
        cv = stdev / mean if mean > 0 else 1  # Coefficient of variation
        if cv < 0.15:
            confidence = "high"
        elif cv < 0.3:
            confidence = "medium"
        else:
            confidence = "low"

        return ConfidenceInterval(
            low=max(0, mean - 1.96 * stdev),
            mid=mean,
            high=mean + 1.96 * stdev,
            confidence=confidence,
        )

    def _cluster_objections(self) -> List[ObjectionCluster]:
        """Cluster similar objections together."""
        if not self.all_objections:
            return []

        # Simple clustering by keyword matching
        clusters: Dict[str, List[str]] = {}
        keywords = {
            "price": ["price", "expensive", "cost", "afford", "budget"],
            "trust": ["trust", "new", "unknown", "risky", "proven"],
            "features": ["feature", "missing", "need", "functionality", "capability"],
            "competition": ["competitor", "alternative", "existing", "switch"],
            "timing": ["time", "now", "later", "ready", "priority"],
        }

        for objection in self.all_objections:
            obj_lower = objection.lower()
            matched = False
            for theme, words in keywords.items():
                if any(word in obj_lower for word in words):
                    if theme not in clusters:
                        clusters[theme] = []
                    clusters[theme].append(objection)
                    matched = True
                    break
            if not matched:
                if "other" not in clusters:
                    clusters["other"] = []
                clusters["other"].append(objection)

        # Convert to ObjectionCluster objects
        result = []
        for theme, examples in sorted(clusters.items(), key=lambda x: -len(x[1])):
            result.append(ObjectionCluster(
                theme=theme.title(),
                count=len(examples),
                examples=list(set(examples))[:5],
                suggested_counter=self._suggest_counter(theme),
            ))

        return result[:5]  # Top 5 clusters

    def _suggest_counter(self, theme: str) -> str:
        """Suggest counter-messaging for objection theme."""
        counters = {
            "price": "Emphasize ROI and time savings. Offer trial or money-back guarantee.",
            "trust": "Lead with social proof, case studies, and security certifications.",
            "features": "Highlight roadmap or offer custom solutions for key accounts.",
            "competition": "Differentiate on unique value prop. Show migration ease.",
            "timing": "Create urgency with limited offers or demonstrate immediate value.",
            "other": "Gather more specific feedback to address this objection type.",
        }
        return counters.get(theme.lower(), counters["other"])

    def _rank_channels(self) -> List[ChannelRanking]:
        """Rank channels by projected performance."""
        rankings = []

        for channel_name, data in self.channel_data.items():
            if not data:
                continue

            cac_values = [d["cac"] for d in data]
            roi_values = [d["roi"] for d in data]
            reach_values = [d["reach"] for d in data]

            cac_ci = self._compute_ci(cac_values, "cac")
            avg_roi = statistics.mean(roi_values) if roi_values else 1.0
            avg_reach = int(statistics.mean(reach_values)) if reach_values else 1000

            # Score: higher ROI, lower CAC = better
            score = (avg_roi * 2) / (cac_ci.mid / 50 + 0.5)  # Normalized score

            rankings.append(ChannelRanking(
                channel=channel_name,
                score=round(score, 2),
                cac=cac_ci,
                roi=round(avg_roi, 2),
                reach=avg_reach,
                rationale=f"ROI {avg_roi:.1f}x at ${cac_ci.mid:.0f} CAC",
            ))

        # Sort by score descending
        rankings.sort(key=lambda x: x.score, reverse=True)
        return rankings

    def _compute_overall_confidence(self) -> float:
        """Compute overall simulation confidence score."""
        if not self.cycle_metrics:
            return 0.3

        factors = []

        # Factor 1: Consistency across cycles
        conv_values = [m.get("conversion_rate", 0) for m in self.cycle_metrics]
        if len(conv_values) > 1 and statistics.mean(conv_values) > 0:
            cv = statistics.stdev(conv_values) / statistics.mean(conv_values)
            factors.append(max(0, 1 - cv))  # Lower variance = higher confidence

        # Factor 2: Sample size
        sample_factor = min(1.0, len(self.cycle_metrics) / 30)
        factors.append(sample_factor)

        # Factor 3: Agent convergence (avg confidence from responses)
        conf_values = [m.get("avg_buyer_confidence", 0.5) for m in self.cycle_metrics]
        factors.append(statistics.mean(conf_values) if conf_values else 0.5)

        return round(statistics.mean(factors), 2) if factors else 0.5

    def _empty_metrics(self) -> SimulationMetrics:
        """Return empty metrics when no data."""
        empty_ci = ConfidenceInterval(0, 0, 0, "low")
        return SimulationMetrics(
            cac=empty_ci,
            conversion_rate=empty_ci,
            ltv=empty_ci,
            time_to_breakeven_months=empty_ci,
            competitive_threat_score=5.0,
            market_readiness_score=5.0,
            overall_confidence=0.0,
            objection_clusters=[],
            channel_rankings=[],
            cycle_metrics=[],
        )
