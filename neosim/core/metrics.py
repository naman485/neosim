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
class ICPMetrics:
    """Per-ICP persona metrics."""
    name: str
    role: str
    company_size: str
    budget_range: str
    pain_points: List[str]
    goals: List[str]

    # Computed metrics
    total_responses: int = 0
    buy_count: int = 0
    pass_count: int = 0
    object_count: int = 0
    conversion_rate: float = 0.0
    avg_confidence: float = 0.0
    objections_raised: List[str] = field(default_factory=list)
    top_objections: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "company_size": self.company_size,
            "budget_range": self.budget_range,
            "pain_points": self.pain_points,
            "goals": self.goals,
            "total_responses": self.total_responses,
            "buy_count": self.buy_count,
            "pass_count": self.pass_count,
            "object_count": self.object_count,
            "conversion_rate": round(self.conversion_rate, 3),
            "avg_confidence": round(self.avg_confidence, 2),
            "top_objections": self.top_objections[:5],
        }


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

    # ICP persona metrics
    icp_metrics: List[ICPMetrics] = field(default_factory=list)

    # Raw data
    cycle_metrics: List[Dict[str, Any]] = field(default_factory=list)

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
            "icp_metrics": [icp.to_dict() for icp in self.icp_metrics],
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
        self.icp_data: Dict[str, Dict[str, Any]] = {}  # Per-ICP tracking

    def add_cycle(self, cycle_result, buyer_agents=None) -> None:
        """
        Add cycle results to aggregation.

        Args:
            cycle_result: CycleResult from simulation
            buyer_agents: List of BuyerAgent instances (for persona info)
        """
        # Store cycle metrics
        self.cycle_metrics.append(cycle_result.metrics)

        # Extract objections and track per-ICP metrics
        for i, response in enumerate(cycle_result.buyer_responses):
            # Get persona info if available
            persona_name = "Unknown"
            persona_info = {}
            if buyer_agents and i < len(buyer_agents):
                agent = buyer_agents[i]
                if hasattr(agent, 'persona'):
                    persona = agent.persona
                    persona_name = persona.name
                    persona_info = {
                        "role": persona.role,
                        "company_size": persona.company_size,
                        "budget_range": persona.budget_range,
                        "pain_points": persona.pain_points,
                        "goals": persona.goals,
                    }

            # Initialize ICP tracking if needed
            if persona_name not in self.icp_data:
                self.icp_data[persona_name] = {
                    "info": persona_info,
                    "responses": [],
                    "objections": [],
                }

            # Track response
            self.icp_data[persona_name]["responses"].append({
                "decision": response.decision,
                "confidence": response.confidence,
            })

            # Extract objections
            for signal in response.signals:
                if signal.startswith("objection:"):
                    objection = signal.replace("objection:", "")
                    self.all_objections.append(objection)
                    self.icp_data[persona_name]["objections"].append(objection)

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

        # Compute ICP metrics
        icp_metrics = self._compute_icp_metrics()

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
            icp_metrics=icp_metrics,
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

    def _compute_icp_metrics(self) -> List[ICPMetrics]:
        """Compute per-ICP persona metrics."""
        results = []

        for persona_name, data in self.icp_data.items():
            responses = data.get("responses", [])
            objections = data.get("objections", [])
            info = data.get("info", {})

            if not responses:
                continue

            buy_count = sum(1 for r in responses if r["decision"] == "BUY")
            pass_count = sum(1 for r in responses if r["decision"] == "PASS")
            object_count = sum(1 for r in responses if r["decision"] == "OBJECT")
            total = len(responses)

            # Compute conversion rate
            conversion_rate = buy_count / total if total > 0 else 0

            # Average confidence
            avg_confidence = (
                sum(r["confidence"] for r in responses) / total
                if total > 0 else 0
            )

            # Find top objections for this persona
            objection_counts: Dict[str, int] = {}
            for obj in objections:
                objection_counts[obj] = objection_counts.get(obj, 0) + 1
            top_objections = sorted(
                objection_counts.keys(),
                key=lambda x: objection_counts[x],
                reverse=True
            )[:5]

            results.append(ICPMetrics(
                name=persona_name,
                role=info.get("role", "Unknown"),
                company_size=info.get("company_size", "Unknown"),
                budget_range=info.get("budget_range", "Unknown"),
                pain_points=info.get("pain_points", []),
                goals=info.get("goals", []),
                total_responses=total,
                buy_count=buy_count,
                pass_count=pass_count,
                object_count=object_count,
                conversion_rate=conversion_rate,
                avg_confidence=avg_confidence,
                objections_raised=objections,
                top_objections=top_objections,
            ))

        # Sort by conversion rate descending
        results.sort(key=lambda x: x.conversion_rate, reverse=True)
        return results

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
