"""
Benchmark Replays - Known launch outcomes for calibration.

These are real product launches with documented outcomes.
Users can run these replays to see how NeoSim predictions
compare to actual results, building trust before their own sims.
"""

BENCHMARKS = {
    "notion-freemium": {
        "name": "Notion Freemium Launch",
        "year": 2018,
        "description": "Notion switched from paid-only to freemium model",
        "actual_outcome": {
            "result": "3x adoption velocity increase",
            "time_to_virality": "6 months",
            "key_driver": "Team collaboration features drove organic spread",
        },
        "config": {
            "product": {
                "name": "Notion",
                "category": "SaaS",
                "description": "All-in-one workspace for notes, docs, and collaboration",
                "unique_value_prop": "Replace 5 tools with one flexible workspace",
            },
            "pricing": {
                "model": "freemium",
                "tiers": [
                    {"name": "Personal", "price": 0},
                    {"name": "Team", "price": 8},
                ],
            },
            "channels": [
                {"name": "product-led", "priority": 5},
                {"name": "community", "priority": 4},
            ],
            "icp_personas": [
                {
                    "name": "Startup Operator",
                    "role": "Ops/PM",
                    "pain_points": ["Tool sprawl", "Documentation chaos"],
                },
            ],
        },
    },
    "superhuman-waitlist": {
        "name": "Superhuman Premium Waitlist",
        "year": 2017,
        "description": "Superhuman launched at $30/mo with manufactured scarcity",
        "actual_outcome": {
            "result": "Premium positioning established, high retention",
            "conversion_rate": "~30% of waitlist",
            "key_driver": "Exclusivity + onboarding calls created word-of-mouth",
        },
        "config": {
            "product": {
                "name": "Superhuman",
                "category": "SaaS",
                "description": "The fastest email experience ever made",
                "unique_value_prop": "100ms response time, keyboard-first",
            },
            "pricing": {
                "model": "paid-only",
                "tiers": [
                    {"name": "Pro", "price": 30},
                ],
            },
            "channels": [
                {"name": "outbound", "priority": 5},  # Personal onboarding
                {"name": "organic-social", "priority": 4},  # Word of mouth
            ],
        },
    },
    "linear-devfirst": {
        "name": "Linear Developer-First Launch",
        "year": 2019,
        "description": "Linear launched with zero marketing, pure product quality",
        "actual_outcome": {
            "result": "80%+ organic adoption, became default for startups",
            "cac": "Near $0",
            "key_driver": "Keyboard shortcuts + speed delighted developers who spread it",
        },
        "config": {
            "product": {
                "name": "Linear",
                "category": "DevTool",
                "description": "Issue tracking built for modern software teams",
                "unique_value_prop": "Fast, keyboard-first, beautiful",
            },
            "pricing": {
                "model": "freemium",
                "tiers": [
                    {"name": "Free", "price": 0},
                    {"name": "Standard", "price": 8},
                ],
            },
            "channels": [
                {"name": "product-led", "priority": 5},
                {"name": "community", "priority": 3},
            ],
        },
    },
}


def get_benchmark(name: str) -> dict:
    """Get a benchmark by name."""
    return BENCHMARKS.get(name)


def list_benchmarks() -> list:
    """List all available benchmarks."""
    return [
        {"id": k, "name": v["name"], "year": v["year"]}
        for k, v in BENCHMARKS.items()
    ]
