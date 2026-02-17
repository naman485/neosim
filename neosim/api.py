"""
NeoSim API Server

FastAPI server wrapping the NeoSim CLI for hosted deployment on CreateOS.
"""

import os
import json
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from .core.config import (
    NeoSimConfig, ProductConfig, ICPPersona, PricingConfig,
    PricingTier, ChannelConfig, CompetitorConfig, SimulationParams
)
from .core.simulation import Simulation
from .execution.distribution import DistributionGenerator


# ============================================================================
# Request/Response Models
# ============================================================================

class ProductInput(BaseModel):
    name: str
    description: str
    category: str = "SaaS"
    stage: str = "pre-launch"
    unique_value_prop: str
    key_features: List[str] = []

class PersonaInput(BaseModel):
    name: str
    role: str
    company_size: str = "startup"
    pain_points: List[str] = []
    goals: List[str] = []
    budget_range: str = "unknown"
    decision_speed: str = "medium"

class PricingTierInput(BaseModel):
    name: str
    price: float
    billing: str = "monthly"
    features: List[str] = []

class PricingInput(BaseModel):
    model: str = "freemium"
    tiers: List[PricingTierInput] = []

class ChannelInput(BaseModel):
    name: str
    priority: int = 3

class CompetitorInput(BaseModel):
    name: str
    positioning: str = ""
    market_share: str = "unknown"

class SimulationRequest(BaseModel):
    """Request body for /api/simulate"""
    project_name: str = "My Product"
    product: ProductInput
    icp_personas: List[PersonaInput] = []
    pricing: PricingInput
    channels: List[ChannelInput] = []
    competitors: List[CompetitorInput] = []
    cycles: int = Field(default=10, ge=1, le=30)
    buyer_agents: int = Field(default=15, ge=5, le=50)

class DistributeRequest(BaseModel):
    """Request body for /api/distribute"""
    simulation_results: Dict[str, Any]
    config: SimulationRequest
    platforms: List[str] = ["twitter", "reddit", "linkedin", "producthunt"]
    calendar_start: Optional[str] = None

class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, str]] = None
    meta: Optional[Dict[str, Any]] = None


# ============================================================================
# App Setup
# ============================================================================

start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown

app = FastAPI(
    title="NeoSim API",
    description="GTM Simulation API - Test your go-to-market strategy before launch",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Helper Functions
# ============================================================================

def request_to_config(req: SimulationRequest) -> NeoSimConfig:
    """Convert API request to NeoSimConfig."""
    config = NeoSimConfig(
        version="1.0",
        project_name=req.project_name,
        created_at=datetime.now().isoformat(),
        llm_provider=os.environ.get("LLM_PROVIDER", "anthropic"),
        llm_model=os.environ.get("LLM_MODEL", "claude-sonnet-4-20250514"),
    )

    # Product
    config.product = ProductConfig(
        name=req.product.name,
        description=req.product.description,
        category=req.product.category,
        stage=req.product.stage,
        unique_value_prop=req.product.unique_value_prop,
        key_features=req.product.key_features,
    )

    # ICP Personas
    config.icp_personas = [
        ICPPersona(
            name=p.name,
            role=p.role,
            company_size=p.company_size,
            pain_points=p.pain_points,
            goals=p.goals,
            budget_range=p.budget_range,
            decision_speed=p.decision_speed,
        )
        for p in req.icp_personas
    ] if req.icp_personas else [
        ICPPersona(
            name="Default Buyer",
            role="Decision Maker",
            company_size="startup",
            pain_points=["Manual processes"],
            goals=["Automate workflows"],
        )
    ]

    # Pricing
    config.pricing = PricingConfig(
        model=req.pricing.model,
        tiers=[
            PricingTier(
                name=t.name,
                price=t.price,
                billing=t.billing,
                features=t.features,
            )
            for t in req.pricing.tiers
        ] if req.pricing.tiers else [
            PricingTier(name="Free", price=0),
            PricingTier(name="Pro", price=29),
        ],
    )

    # Channels
    config.channels = [
        ChannelConfig(name=c.name, priority=c.priority)
        for c in req.channels
    ] if req.channels else [
        ChannelConfig(name="organic-social", priority=5),
    ]

    # Competitors
    config.competitors = [
        CompetitorConfig(
            name=c.name,
            positioning=c.positioning,
            market_share=c.market_share,
        )
        for c in req.competitors
    ]

    # Simulation params
    config.simulation = SimulationParams(
        cycles=req.cycles,
        buyer_agents=req.buyer_agents,
    )

    return config


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Service info."""
    return {
        "name": "neosim-api",
        "version": "1.0.0",
        "description": "GTM Simulation API - Test your go-to-market strategy with AI agents",
        "pricing": {
            "simulate": {"credits": 50, "usd": "$0.50"},
            "distribute": {"credits": 20, "usd": "$0.20"},
        },
        "endpoints": [
            {"method": "POST", "path": "/api/simulate", "description": "Run GTM simulation"},
            {"method": "POST", "path": "/api/distribute", "description": "Generate distribution kit"},
        ],
        "docs": "/docs",
        "health": "/health",
        "mcp": "/mcp-tool.json",
    }


@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "ok",
        "uptime": int(time.time() - start_time),
        "version": "1.0.0",
    }


@app.get("/mcp-tool.json")
async def mcp_tool():
    """MCP tool definition for AI agent discovery."""
    return {
        "tools": [
            {
                "name": "neosim_simulate",
                "description": "Run a GTM (go-to-market) simulation for a product. Returns projected CAC, conversion rates, buyer objections, and channel rankings.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string", "description": "Name of the project"},
                        "product": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "unique_value_prop": {"type": "string"},
                            },
                            "required": ["name", "description", "unique_value_prop"],
                        },
                        "pricing": {
                            "type": "object",
                            "properties": {
                                "model": {"type": "string", "enum": ["freemium", "free-trial", "paid-only"]},
                                "tiers": {"type": "array"},
                            },
                        },
                        "cycles": {"type": "integer", "minimum": 1, "maximum": 30},
                    },
                    "required": ["product"],
                },
                "endpoint": "POST /api/simulate",
                "pricing": {"credits": 50, "usd": 0.50},
            },
            {
                "name": "neosim_distribute",
                "description": "Generate ready-to-post content for Twitter, Reddit, LinkedIn, and Product Hunt from simulation results.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "simulation_results": {"type": "object", "description": "Results from neosim_simulate"},
                        "platforms": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["simulation_results"],
                },
                "endpoint": "POST /api/distribute",
                "pricing": {"credits": 20, "usd": 0.20},
            },
        ],
    }


@app.get("/docs", response_class=HTMLResponse)
async def docs():
    """API documentation."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeoSim API Docs</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            line-height: 1.6;
            padding: 2rem;
        }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { color: #00d9ff; margin-bottom: 0.5rem; }
        h2 { color: #00d9ff; margin: 2rem 0 1rem; border-bottom: 1px solid #333; padding-bottom: 0.5rem; }
        h3 { color: #888; margin: 1.5rem 0 0.5rem; }
        .subtitle { color: #888; margin-bottom: 2rem; }
        pre {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 1rem;
            overflow-x: auto;
            font-size: 0.9rem;
        }
        code { color: #00d9ff; }
        .endpoint {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .method {
            display: inline-block;
            background: #0a3;
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.8rem;
        }
        .path { color: #00d9ff; font-family: monospace; margin-left: 0.5rem; }
        .credits { color: #f90; }
    </style>
</head>
<body>
    <div class="container">
        <h1>NeoSim API</h1>
        <p class="subtitle">GTM Simulation API - Test your go-to-market strategy with AI agents</p>

        <h2>Endpoints</h2>

        <div class="endpoint">
            <span class="method">POST</span>
            <span class="path">/api/simulate</span>
            <span class="credits">50 credits ($0.50)</span>
            <p style="margin-top: 0.5rem;">Run a GTM simulation with AI buyer, competitor, and channel agents.</p>
        </div>

        <h3>Example Request</h3>
        <pre><code>curl -X POST https://neosim.nodeops.app/api/simulate \\
  -H "Content-Type: application/json" \\
  -d '{
    "project_name": "My Startup",
    "product": {
      "name": "AwesomeApp",
      "description": "AI-powered productivity tool",
      "unique_value_prop": "10x faster with AI",
      "category": "SaaS",
      "stage": "pre-launch"
    },
    "icp_personas": [
      {
        "name": "Technical Founder",
        "role": "Founder/CTO",
        "company_size": "startup",
        "pain_points": ["Manual tasks", "Scaling issues"],
        "goals": ["Ship faster"]
      }
    ],
    "pricing": {
      "model": "freemium",
      "tiers": [
        {"name": "Free", "price": 0},
        {"name": "Pro", "price": 29}
      ]
    },
    "channels": [
      {"name": "organic-social", "priority": 5},
      {"name": "community", "priority": 4}
    ],
    "cycles": 10,
    "buyer_agents": 15
  }'</code></pre>

        <div class="endpoint">
            <span class="method">POST</span>
            <span class="path">/api/distribute</span>
            <span class="credits">20 credits ($0.20)</span>
            <p style="margin-top: 0.5rem;">Generate ready-to-post content for Twitter, Reddit, LinkedIn, Product Hunt.</p>
        </div>

        <h2>Response Format</h2>
        <pre><code>{
  "success": true,
  "data": { ... },
  "meta": {
    "credits": 50,
    "processingMs": 12500
  }
}</code></pre>

        <h2>Open Source</h2>
        <p>NeoSim is open source. Run it locally with your own API keys:</p>
        <pre><code>pip install neosim
export ANTHROPIC_API_KEY=sk-ant-...
neosim init
neosim sim</code></pre>
        <p style="margin-top: 1rem;"><a href="https://github.com/naman485/neosim" style="color: #00d9ff;">GitHub Repository</a></p>
    </div>
</body>
</html>"""


@app.post("/api/simulate")
async def simulate(request: SimulationRequest):
    """
    Run a GTM simulation.

    Returns projected metrics, buyer objections, channel rankings, and recommendations.
    """
    start = time.time()

    try:
        # Convert request to config
        config = request_to_config(request)

        # Validate
        issues = config.validate()
        if issues:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": {"code": "INVALID_CONFIG", "message": "; ".join(issues)},
                },
            )

        # Run simulation
        simulation = Simulation(config)
        result = simulation.run()

        # Build response
        response_data = {
            "sim_id": result.sim_id,
            "overall_assessment": result.overall_assessment,
            "confidence_score": result.confidence_score,
            "metrics": result.final_metrics.to_dict(),
            "recommendations": result.top_recommendations,
            "risks": result.top_risks,
        }

        processing_ms = int((time.time() - start) * 1000)

        return {
            "success": True,
            "data": response_data,
            "meta": {"credits": 50, "processingMs": processing_ms},
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {"code": "SIMULATION_ERROR", "message": str(e)},
            },
        )


@app.post("/api/distribute")
async def distribute(request: DistributeRequest):
    """
    Generate distribution kit from simulation results.

    Returns ready-to-post content for selected platforms.
    """
    start = time.time()

    try:
        # Reconstruct config and result
        config = request_to_config(request.config)

        # Create mock result object for generator
        from .core.metrics import (
            SimulationMetrics, ConfidenceInterval,
            ObjectionCluster, ChannelRanking
        )

        metrics_data = request.simulation_results.get("metrics", {})

        def ci_from_dict(d):
            return ConfidenceInterval(
                low=d.get("low", 0),
                mid=d.get("mid", 0),
                high=d.get("high", 0),
                confidence=d.get("confidence", "low"),
            )

        metrics = SimulationMetrics(
            cac=ci_from_dict(metrics_data.get("cac", {})),
            conversion_rate=ci_from_dict(metrics_data.get("conversion_rate", {})),
            ltv=ci_from_dict(metrics_data.get("ltv", {})),
            time_to_breakeven_months=ci_from_dict(metrics_data.get("time_to_breakeven_months", {})),
            competitive_threat_score=metrics_data.get("competitive_threat_score", 5),
            market_readiness_score=metrics_data.get("market_readiness_score", 5),
            overall_confidence=request.simulation_results.get("confidence_score", 0.5),
            objection_clusters=[
                ObjectionCluster(
                    theme=o.get("theme", ""),
                    count=o.get("count", 0),
                    examples=o.get("examples", []),
                    suggested_counter=o.get("suggested_counter", ""),
                )
                for o in metrics_data.get("objection_clusters", [])
            ],
            channel_rankings=[
                ChannelRanking(
                    channel=c.get("channel", ""),
                    score=c.get("score", 0),
                    cac=ci_from_dict(c.get("cac", {})),
                    roi=c.get("roi", 1),
                    reach=c.get("reach", 0),
                    rationale=c.get("rationale", ""),
                )
                for c in metrics_data.get("channel_rankings", [])
            ],
            cycle_metrics=[],
        )

        class MockResult:
            def __init__(self):
                self.sim_id = request.simulation_results.get("sim_id", "unknown")
                self.final_metrics = metrics

        # Generate distribution kit
        generator = DistributionGenerator(
            MockResult(),
            config,
            platforms=request.platforms,
        )
        kit = generator.generate()

        # Convert to dict
        kit_data = generator.to_dict()

        processing_ms = int((time.time() - start) * 1000)

        return {
            "success": True,
            "data": kit_data,
            "meta": {"credits": 20, "processingMs": processing_ms},
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {"code": "DISTRIBUTION_ERROR", "message": str(e)},
            },
        )


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
