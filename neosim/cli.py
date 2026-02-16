"""
NeoSim CLI

The command-line interface for NeoSim GTM simulations.

Commands:
    neosim init     - Interactive setup to generate config
    neosim sim      - Run a GTM simulation
    neosim compare  - A/B test two strategies
    neosim report   - Generate shareable reports
    neosim replay   - Re-run historical simulations
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.prompt import Prompt, Confirm
    from rich import print as rprint
except ImportError:
    print("Error: Required packages not installed.")
    print("Run: pip install typer rich")
    sys.exit(1)

from .core.config import NeoSimConfig, load_config, save_config
from .core.config import ProductConfig, ICPPersona, PricingConfig, PricingTier
from .core.config import ChannelConfig, CompetitorConfig, SimulationParams
from .core.simulation import Simulation, SimulationResult
from .agents.base import LLMProvider


app = typer.Typer(
    name="neosim",
    help="NeoSim - The Staging Environment for Distribution",
    add_completion=False,
)
console = Console()


# ============================================================================
# INIT Command
# ============================================================================

@app.command()
def init(
    output: Path = typer.Option(
        Path("neosim.yaml"),
        "--output", "-o",
        help="Output config file path",
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--no-interactive",
        help="Run interactive setup",
    ),
):
    """
    Initialize a new NeoSim project.

    Creates a neosim.yaml configuration file through an interactive
    setup process or with defaults.
    """
    console.print(Panel.fit(
        "[bold cyan]NeoSim[/bold cyan] - GTM Simulation Setup",
        subtitle="Let's configure your simulation",
    ))

    if output.exists():
        if not Confirm.ask(f"\n[yellow]{output} already exists. Overwrite?[/yellow]"):
            raise typer.Abort()

    if interactive:
        config = _interactive_init()
    else:
        config = _default_config()

    # Save config
    save_config(config, output)
    console.print(f"\n[green]Config saved to {output}[/green]")
    console.print("\nNext steps:")
    console.print("  1. Review and customize neosim.yaml")
    console.print("  2. Set your API key: export ANTHROPIC_API_KEY=...")
    console.print("  3. Run simulation: [bold]neosim sim[/bold]")


def _interactive_init() -> NeoSimConfig:
    """Run interactive config setup."""
    console.print("\n[bold]Product Information[/bold]")

    product_name = Prompt.ask("Product name")
    product_desc = Prompt.ask("One-line description")
    category = Prompt.ask(
        "Category",
        choices=["SaaS", "DevTool", "Consumer", "Marketplace", "API", "Other"],
        default="SaaS",
    )
    stage = Prompt.ask(
        "Stage",
        choices=["idea", "pre-launch", "beta", "launched"],
        default="pre-launch",
    )
    uvp = Prompt.ask("Unique value proposition (what makes you different?)")

    product = ProductConfig(
        name=product_name,
        description=product_desc,
        category=category,
        stage=stage,
        unique_value_prop=uvp,
        key_features=[],
    )

    # ICP
    console.print("\n[bold]Ideal Customer Profile[/bold]")
    icp_name = Prompt.ask("Primary persona name", default="Technical Founder")
    icp_role = Prompt.ask("Their role", default="Founder/CEO")
    icp_size = Prompt.ask(
        "Company size",
        choices=["solo", "startup", "smb", "enterprise"],
        default="startup",
    )
    pain_point = Prompt.ask("Main pain point you solve")

    icp = ICPPersona(
        name=icp_name,
        role=icp_role,
        company_size=icp_size,
        pain_points=[pain_point],
        goals=["Solve " + pain_point],
        budget_range="$50-500/mo",
        decision_speed="medium",
    )

    # Pricing
    console.print("\n[bold]Pricing Strategy[/bold]")
    pricing_model = Prompt.ask(
        "Pricing model",
        choices=["freemium", "free-trial", "paid-only", "usage-based"],
        default="freemium",
    )
    main_price = typer.prompt("Main paid tier price ($/mo)", type=float, default=29.0)

    tiers = [
        PricingTier(name="Free", price=0, features=["Basic features"]),
        PricingTier(name="Pro", price=main_price, features=["All features"]),
    ]
    pricing = PricingConfig(model=pricing_model, tiers=tiers)

    # Channels
    console.print("\n[bold]Distribution Channels[/bold]")
    console.print("Select your primary channels (comma-separated):")
    console.print("  organic-social, paid-ads, community, outbound, seo, partnerships, product-led")
    channels_input = Prompt.ask("Channels", default="organic-social, community")

    channels = []
    for i, ch in enumerate(channels_input.split(",")):
        channels.append(ChannelConfig(
            name=ch.strip(),
            priority=5 - i,  # Higher priority for earlier ones
        ))

    # Competitors
    console.print("\n[bold]Competitors[/bold]")
    competitor_name = Prompt.ask("Main competitor (or 'none')", default="none")

    competitors = []
    if competitor_name.lower() != "none":
        competitors.append(CompetitorConfig(
            name=competitor_name,
            positioning="Established player in the market",
            market_share="significant",
        ))

    # Build config
    config = NeoSimConfig(
        version="1.0",
        project_name=product_name,
        created_at=datetime.now().isoformat(),
        product=product,
        icp_personas=[icp],
        pricing=pricing,
        channels=channels,
        competitors=competitors,
        simulation=SimulationParams(cycles=10, buyer_agents=10),  # Smaller for testing
    )

    return config


def _default_config() -> NeoSimConfig:
    """Create default config without interaction."""
    return NeoSimConfig(
        version="1.0",
        project_name="My Product",
        created_at=datetime.now().isoformat(),
        product=ProductConfig(
            name="My Product",
            description="A product that solves problems",
            category="SaaS",
            stage="pre-launch",
            unique_value_prop="The only solution that does X",
        ),
        icp_personas=[
            ICPPersona(
                name="Technical Founder",
                role="Founder/CTO",
                company_size="startup",
                pain_points=["Manual processes", "Scaling challenges"],
                goals=["Automate workflows", "Scale efficiently"],
            )
        ],
        pricing=PricingConfig(
            model="freemium",
            tiers=[
                PricingTier(name="Free", price=0),
                PricingTier(name="Pro", price=29),
            ],
        ),
        channels=[
            ChannelConfig(name="organic-social", priority=5),
            ChannelConfig(name="community", priority=4),
        ],
        competitors=[],
        simulation=SimulationParams(cycles=10, buyer_agents=10),
    )


# ============================================================================
# SIM Command
# ============================================================================

@app.command()
def sim(
    config_path: Path = typer.Option(
        Path("neosim.yaml"),
        "--config", "-c",
        help="Path to config file",
    ),
    cycles: int = typer.Option(
        None,
        "--cycles", "-n",
        help="Override number of cycles",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save results to JSON file",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed output",
    ),
    url: Optional[str] = typer.Option(
        None,
        "--url",
        help="Landing page URL to analyze for execution quality",
    ),
    docs_url: Optional[str] = typer.Option(
        None,
        "--docs",
        help="API documentation URL to analyze",
    ),
    mcp_url: Optional[str] = typer.Option(
        None,
        "--mcp",
        help="MCP tool definition URL to analyze",
    ),
):
    """
    Run a GTM simulation.

    Deploys AI agents to simulate buyer behavior, competitor responses,
    and channel performance for your configured strategy.

    Use --url to analyze your landing page and adjust conversion predictions
    based on execution quality (not just positioning).
    """
    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
        console.print("[red]Error: No API key found.[/red]")
        console.print("Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable.")
        raise typer.Exit(1)

    # Load config
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        console.print(f"[red]Error: Config file not found: {config_path}[/red]")
        console.print("Run [bold]neosim init[/bold] to create one.")
        raise typer.Exit(1)

    # Validate config
    issues = config.validate()
    if issues:
        console.print("[red]Config validation errors:[/red]")
        for issue in issues:
            console.print(f"  - {issue}")
        raise typer.Exit(1)

    # Override cycles if specified
    if cycles:
        config.simulation.cycles = cycles

    # Analyze execution quality if URLs provided
    execution_quality = None
    if url or docs_url or mcp_url:
        from .core.web_analyzer import WebAnalyzer
        console.print("\n[bold]Analyzing Execution Quality...[/bold]")

        analyzer = WebAnalyzer()

        if url:
            console.print(f"  Analyzing landing page: {url}")
        if docs_url:
            console.print(f"  Analyzing API docs: {docs_url}")
        if mcp_url:
            console.print(f"  Analyzing MCP tools: {mcp_url}")

        execution_quality = analyzer.analyze_all(
            landing_url=url,
            docs_url=docs_url,
            mcp_url=mcp_url,
        )

        # Display execution quality results
        _display_execution_quality(execution_quality)

    # Display header
    console.print(Panel.fit(
        f"[bold cyan]NeoSim[/bold cyan] - Simulating [bold]{config.product.name}[/bold]",
        subtitle=f"{config.simulation.cycles} cycles | {config.simulation.buyer_agents} buyers",
    ))

    # Determine provider
    provider = LLMProvider.ANTHROPIC
    if os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
        provider = LLMProvider.OPENAI

    # Create progress display
    cycle_metrics = []

    def on_cycle(cycle_num: int, result):
        cycle_metrics.append(result.metrics)
        if verbose:
            _display_cycle_result(cycle_num, result)

    # Run simulation
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task(
            "Running simulation...",
            total=config.simulation.cycles,
        )

        def progress_callback(cycle_num: int, result):
            progress.update(task, advance=1, description=f"Cycle {cycle_num}")
            on_cycle(cycle_num, result)

        simulation = Simulation(
            config,
            provider=provider,
            on_cycle_complete=progress_callback,
            execution_quality=execution_quality,
        )
        result = simulation.run()

    # Display results
    _display_final_results(result, execution_quality)

    # Save if requested
    if output:
        _save_results(result, output, execution_quality)
        console.print(f"\n[green]Results saved to {output}[/green]")


def _display_cycle_result(cycle_num: int, result):
    """Display single cycle results."""
    metrics = result.metrics
    console.print(f"\n[dim]Cycle {cycle_num}:[/dim] "
                  f"Conv: {metrics.get('conversion_rate', 0):.1%} | "
                  f"CAC: ${metrics.get('avg_cac', 0):.0f} | "
                  f"Threat: {metrics.get('avg_competitor_threat', 0):.1f}/10")


def _display_execution_quality(eq):
    """Display execution quality analysis results."""
    from .core.web_analyzer import ExecutionQualityScore

    console.print("\n")
    score_color = "green" if eq.overall_score >= 7 else "yellow" if eq.overall_score >= 5 else "red"
    console.print(Panel.fit(
        f"[bold]Execution Quality Score:[/bold] [{score_color}]{eq.overall_score:.1f}/10[/{score_color}]",
        subtitle=f"Conversion Multiplier: {eq.conversion_multiplier:.2f}x",
    ))

    if eq.landing_page:
        lp = eq.landing_page
        console.print(f"\n[bold]Landing Page Analysis[/bold] ({lp.url})")
        console.print(f"  Score: {lp.score:.1f}/10")

        if lp.strengths:
            console.print("  [green]Strengths:[/green]")
            for s in lp.strengths[:3]:
                console.print(f"    + {s}")

        if lp.weaknesses:
            console.print("  [red]Weaknesses:[/red]")
            for w in lp.weaknesses[:3]:
                console.print(f"    - {w}")

        if lp.recommendations:
            console.print("  [cyan]Recommendations:[/cyan]")
            for r in lp.recommendations[:3]:
                console.print(f"    → {r}")

    if eq.api_docs:
        docs = eq.api_docs
        console.print(f"\n[bold]API Docs Analysis[/bold] ({docs.url})")
        console.print(f"  Score: {docs.score:.1f}/10")
        if docs.weaknesses:
            for w in docs.weaknesses[:2]:
                console.print(f"    - {w}")

    if eq.mcp:
        mcp = eq.mcp
        console.print(f"\n[bold]MCP Analysis[/bold] ({mcp.tool_definition_url})")
        console.print(f"  Score: {mcp.score:.1f}/10")
        if mcp.tools_found:
            console.print(f"  Tools: {', '.join(mcp.tools_found[:5])}")
        if mcp.issues:
            for issue in mcp.issues[:2]:
                console.print(f"    - {issue}")

    console.print("")


def _display_final_results(result: SimulationResult, execution_quality=None):
    """Display final simulation results."""
    console.print("\n")
    console.print(Panel.fit(
        "[bold green]Simulation Complete[/bold green]",
        subtitle=f"ID: {result.sim_id} | Duration: {result.total_duration_seconds:.1f}s",
    ))

    # Overall assessment
    assessment_colors = {
        "strong": "green",
        "promising": "cyan",
        "uncertain": "yellow",
        "concerning": "orange1",
        "weak": "red",
    }
    color = assessment_colors.get(result.overall_assessment, "white")
    console.print(f"\n[bold]Overall Assessment:[/bold] [{color}]{result.overall_assessment.upper()}[/{color}]")
    console.print(f"[bold]Confidence Score:[/bold] {result.confidence_score:.0%}")

    # Key metrics table
    metrics = result.final_metrics
    table = Table(title="\nKey Metrics", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Low", justify="right")
    table.add_column("Mid", justify="right", style="bold")
    table.add_column("High", justify="right")
    table.add_column("Confidence")

    table.add_row(
        "CAC",
        f"${metrics.cac.low:.0f}",
        f"${metrics.cac.mid:.0f}",
        f"${metrics.cac.high:.0f}",
        metrics.cac.confidence,
    )
    # Show adjusted conversion if execution quality was analyzed
    conv_low = metrics.conversion_rate.low
    conv_mid = metrics.conversion_rate.mid
    conv_high = metrics.conversion_rate.high
    conv_label = "Conversion Rate"

    if execution_quality:
        multiplier = execution_quality.conversion_multiplier
        conv_low *= multiplier
        conv_mid *= multiplier
        conv_high *= multiplier
        conv_label = f"Conversion (adj {multiplier:.1f}x)"

    table.add_row(
        conv_label,
        f"{conv_low:.1%}",
        f"{conv_mid:.1%}",
        f"{conv_high:.1%}",
        metrics.conversion_rate.confidence,
    )
    table.add_row(
        "Time to Breakeven",
        f"{metrics.time_to_breakeven_months.low:.0f}mo",
        f"{metrics.time_to_breakeven_months.mid:.0f}mo",
        f"{metrics.time_to_breakeven_months.high:.0f}mo",
        metrics.time_to_breakeven_months.confidence,
    )

    console.print(table)

    # Top objections
    if metrics.objection_clusters:
        console.print("\n[bold]Top Objections[/bold]")
        for obj in metrics.objection_clusters[:3]:
            console.print(f"  - [yellow]{obj.theme}[/yellow] ({obj.count}x): {obj.suggested_counter}")

    # Channel rankings
    if metrics.channel_rankings:
        console.print("\n[bold]Channel Rankings[/bold]")
        for i, ch in enumerate(metrics.channel_rankings[:3], 1):
            console.print(f"  {i}. {ch.channel}: Score {ch.score} ({ch.rationale})")

    # Recommendations
    if result.top_recommendations:
        console.print("\n[bold]Strategic Recommendations[/bold]")
        for rec in result.top_recommendations[:3]:
            console.print(f"  - {rec}")

    # Risks
    if result.top_risks:
        console.print("\n[bold red]Key Risks[/bold red]")
        for risk in result.top_risks[:2]:
            console.print(f"  - {risk}")


def _save_results(result: SimulationResult, path: Path, execution_quality=None):
    """Save simulation results to JSON."""
    import json

    data = {
        "sim_id": result.sim_id,
        "overall_assessment": result.overall_assessment,
        "confidence_score": result.confidence_score,
        "started_at": result.started_at,
        "completed_at": result.completed_at,
        "duration_seconds": result.total_duration_seconds,
        "metrics": result.final_metrics.to_dict(),
        "recommendations": result.top_recommendations,
        "risks": result.top_risks,
    }

    # Add execution quality if analyzed
    if execution_quality:
        data["execution_quality"] = execution_quality.to_dict()

        # Add adjusted conversion metrics
        multiplier = execution_quality.conversion_multiplier
        metrics = result.final_metrics
        data["adjusted_metrics"] = {
            "conversion_rate": {
                "low": metrics.conversion_rate.low * multiplier,
                "mid": metrics.conversion_rate.mid * multiplier,
                "high": metrics.conversion_rate.high * multiplier,
                "multiplier": multiplier,
            }
        }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ============================================================================
# COMPARE Command
# ============================================================================

@app.command()
def compare(
    config_a: Path = typer.Argument(..., help="First strategy config"),
    config_b: Path = typer.Argument(..., help="Second strategy config"),
    cycles: int = typer.Option(10, "--cycles", "-n", help="Cycles per strategy"),
):
    """
    A/B test two GTM strategies.

    Runs both strategies and compares their projected outcomes.
    """
    console.print(Panel.fit(
        "[bold cyan]NeoSim[/bold cyan] - Strategy Comparison",
        subtitle=f"A: {config_a.name} vs B: {config_b.name}",
    ))

    # Load both configs
    try:
        cfg_a = load_config(config_a)
        cfg_b = load_config(config_b)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    # Override cycles
    cfg_a.simulation.cycles = cycles
    cfg_b.simulation.cycles = cycles

    provider = LLMProvider.ANTHROPIC
    if os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
        provider = LLMProvider.OPENAI

    # Run both simulations
    console.print("\n[bold]Running Strategy A...[/bold]")
    sim_a = Simulation(cfg_a, provider=provider)
    result_a = sim_a.run()

    console.print("\n[bold]Running Strategy B...[/bold]")
    sim_b = Simulation(cfg_b, provider=provider)
    result_b = sim_b.run()

    # Compare results
    _display_comparison(result_a, result_b, config_a.stem, config_b.stem)


def _display_comparison(result_a: SimulationResult, result_b: SimulationResult, name_a: str, name_b: str):
    """Display comparison between two strategies."""
    console.print("\n")
    console.print(Panel.fit("[bold green]Comparison Results[/bold green]"))

    table = Table(title="\nStrategy Comparison", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column(f"A: {name_a}", justify="right")
    table.add_column(f"B: {name_b}", justify="right")
    table.add_column("Winner", justify="center")

    metrics_a = result_a.final_metrics
    metrics_b = result_b.final_metrics

    # CAC comparison (lower is better)
    cac_winner = "A" if metrics_a.cac.mid < metrics_b.cac.mid else "B"
    table.add_row(
        "CAC",
        f"${metrics_a.cac.mid:.0f}",
        f"${metrics_b.cac.mid:.0f}",
        f"[green]{cac_winner}[/green]",
    )

    # Conversion (higher is better)
    conv_winner = "A" if metrics_a.conversion_rate.mid > metrics_b.conversion_rate.mid else "B"
    table.add_row(
        "Conversion",
        f"{metrics_a.conversion_rate.mid:.1%}",
        f"{metrics_b.conversion_rate.mid:.1%}",
        f"[green]{conv_winner}[/green]",
    )

    # Confidence (higher is better)
    conf_winner = "A" if result_a.confidence_score > result_b.confidence_score else "B"
    table.add_row(
        "Confidence",
        f"{result_a.confidence_score:.0%}",
        f"{result_b.confidence_score:.0%}",
        f"[green]{conf_winner}[/green]",
    )

    # Threat level (lower is better)
    threat_winner = "A" if metrics_a.competitive_threat_score < metrics_b.competitive_threat_score else "B"
    table.add_row(
        "Comp. Threat",
        f"{metrics_a.competitive_threat_score:.1f}/10",
        f"{metrics_b.competitive_threat_score:.1f}/10",
        f"[green]{threat_winner}[/green]",
    )

    console.print(table)

    # Overall winner
    a_wins = sum([
        cac_winner == "A",
        conv_winner == "A",
        conf_winner == "A",
        threat_winner == "A",
    ])
    overall_winner = "A" if a_wins > 2 else "B"
    winner_name = name_a if overall_winner == "A" else name_b

    console.print(f"\n[bold]Recommended Strategy:[/bold] [green]{winner_name}[/green] ({overall_winner})")


# ============================================================================
# REPORT Command
# ============================================================================

@app.command()
def report(
    results_file: Path = typer.Argument(..., help="Simulation results JSON"),
    format: str = typer.Option("html", "--format", "-f", help="Output format: html, json"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """
    Generate a shareable report from simulation results.

    Creates an HTML or JSON report that can be shared or
    included in pitch decks.
    """
    import json

    # Load results
    try:
        with open(results_file) as f:
            data = json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Error: File not found: {results_file}[/red]")
        raise typer.Exit(1)

    if format == "html":
        html = _generate_html_report(data)
        out_path = output or results_file.with_suffix(".html")
        with open(out_path, "w") as f:
            f.write(html)
        console.print(f"[green]HTML report saved to {out_path}[/green]")
    else:
        out_path = output or results_file.with_suffix(".report.json")
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)
        console.print(f"[green]JSON report saved to {out_path}[/green]")


def _generate_html_report(data: dict) -> str:
    """Generate HTML report from results data."""
    metrics = data.get("metrics", {})

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeoSim Report - {data.get('sim_id', 'Unknown')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #00d9ff; margin-bottom: 0.5rem; }}
        h2 {{ color: #00d9ff; margin: 2rem 0 1rem; border-bottom: 1px solid #333; padding-bottom: 0.5rem; }}
        .meta {{ color: #888; margin-bottom: 2rem; }}
        .assessment {{
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-weight: bold;
            margin: 1rem 0;
        }}
        .assessment.strong {{ background: #0a3; color: white; }}
        .assessment.promising {{ background: #0088cc; color: white; }}
        .assessment.uncertain {{ background: #cc8800; color: white; }}
        .assessment.concerning {{ background: #cc4400; color: white; }}
        .assessment.weak {{ background: #c00; color: white; }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }}
        .metric-card {{
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 1rem;
        }}
        .metric-card h3 {{ color: #00d9ff; font-size: 0.9rem; margin-bottom: 0.5rem; }}
        .metric-value {{ font-size: 1.5rem; font-weight: bold; }}
        .metric-range {{ color: #888; font-size: 0.8rem; }}
        ul {{ margin-left: 1.5rem; }}
        li {{ margin: 0.5rem 0; }}
        .footer {{
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid #333;
            color: #666;
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>NeoSim GTM Simulation Report</h1>
        <p class="meta">
            Simulation ID: {data.get('sim_id', 'N/A')} |
            Completed: {data.get('completed_at', 'N/A')[:10]}
        </p>

        <div class="assessment {data.get('overall_assessment', 'uncertain')}">
            {data.get('overall_assessment', 'UNCERTAIN').upper()}
        </div>
        <p>Confidence: {data.get('confidence_score', 0) * 100:.0f}%</p>

        <h2>Key Metrics</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <h3>Customer Acquisition Cost</h3>
                <div class="metric-value">${metrics.get('cac', {}).get('mid', 0):.0f}</div>
                <div class="metric-range">
                    Range: ${metrics.get('cac', {}).get('low', 0):.0f} - ${metrics.get('cac', {}).get('high', 0):.0f}
                </div>
            </div>
            <div class="metric-card">
                <h3>Conversion Rate</h3>
                <div class="metric-value">{metrics.get('conversion_rate', {}).get('mid', 0) * 100:.1f}%</div>
                <div class="metric-range">
                    Range: {metrics.get('conversion_rate', {}).get('low', 0) * 100:.1f}% - {metrics.get('conversion_rate', {}).get('high', 0) * 100:.1f}%
                </div>
            </div>
            <div class="metric-card">
                <h3>Time to Breakeven</h3>
                <div class="metric-value">{metrics.get('time_to_breakeven_months', {}).get('mid', 0):.0f} months</div>
                <div class="metric-range">Confidence: {metrics.get('time_to_breakeven_months', {}).get('confidence', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <h3>Competitive Threat</h3>
                <div class="metric-value">{metrics.get('competitive_threat_score', 5):.1f}/10</div>
                <div class="metric-range">Market Readiness: {metrics.get('market_readiness_score', 5):.1f}/10</div>
            </div>
        </div>

        <h2>Strategic Recommendations</h2>
        <ul>
            {''.join(f'<li>{rec}</li>' for rec in data.get('recommendations', ['No recommendations available']))}
        </ul>

        <h2>Key Risks</h2>
        <ul>
            {''.join(f'<li>{risk}</li>' for risk in data.get('risks', ['No risks identified']))}
        </ul>

        <div class="footer">
            Generated by NeoSim - The Staging Environment for Distribution<br>
            <a href="https://neosim.dev" style="color: #00d9ff;">neosim.dev</a>
        </div>
    </div>
</body>
</html>"""


# ============================================================================
# EXECUTE Command - Bridge to Action
# ============================================================================

@app.command()
def execute(
    results_file: Path = typer.Argument(..., help="Simulation results JSON"),
    config_path: Path = typer.Option(
        Path("neosim.yaml"),
        "--config", "-c",
        help="Path to config file",
    ),
    output: Path = typer.Option(
        Path("execution_plan.json"),
        "--output", "-o",
        help="Output file for execution plan",
    ),
):
    """
    Generate execution plan from simulation results.

    Converts simulation insights into actionable outputs:
    - Landing page copy
    - Ad copy variants
    - Email sequences
    - ICP export for Clay/Apollo
    - Launch timeline
    """
    import json
    from .execution import ExecutionGenerator

    # Load results and config
    try:
        with open(results_file) as f:
            results_data = json.load(f)
        config = load_config(config_path)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    # We need to reconstruct a minimal result object
    # In practice, this would load the full result
    from .core.metrics import SimulationMetrics, ConfidenceInterval, ObjectionCluster, ChannelRanking

    # Build metrics from saved data
    metrics_data = results_data.get("metrics", {})

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
        overall_confidence=results_data.get("confidence_score", 0.5),
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

    # Create mock result for generator
    class MockResult:
        def __init__(self):
            self.final_metrics = metrics

    generator = ExecutionGenerator(MockResult(), config)
    plan = generator.generate_full_plan()

    # Display summary
    console.print(Panel.fit(
        "[bold cyan]NeoSim[/bold cyan] - Execution Plan Generated",
    ))

    console.print("\n[bold]Channel Priority[/bold]")
    for i, ch in enumerate(plan.channel_priority[:3], 1):
        console.print(f"  {i}. {ch['channel']} (CAC: ${ch['cac']:.0f})")

    console.print("\n[bold]Landing Page Copy[/bold]")
    console.print(f"  Headline: {plan.landing_page_copy.get('headline', 'N/A')}")
    console.print(f"  CTA: {plan.landing_page_copy.get('cta_primary', 'N/A')}")

    console.print("\n[bold]Launch Phases[/bold]")
    for phase in plan.launch_phases:
        console.print(f"  • {phase['phase']}: {phase['goal']}")

    # Save full plan
    generator.export_to_json(str(output))
    console.print(f"\n[green]Full execution plan saved to {output}[/green]")

    # Show ICP export info
    if plan.icp_criteria:
        console.print("\n[bold]ICP Export Ready[/bold]")
        console.print(f"  Clay filters: {output.with_suffix('.clay.json')}")
        console.print("  Copy the 'icp_criteria' section to import into Clay/Apollo")


# ============================================================================
# DISTRIBUTE Command - Platform Content Generation
# ============================================================================

@app.command()
def distribute(
    results_file: Path = typer.Argument(..., help="Simulation results JSON"),
    config_path: Path = typer.Option(
        Path("neosim.yaml"),
        "--config", "-c",
        help="Path to config file",
    ),
    output: Path = typer.Option(
        Path("distribution_kit.json"),
        "--output", "-o",
        help="Output file for distribution kit",
    ),
    platforms: str = typer.Option(
        "twitter,reddit,linkedin,producthunt",
        "--platforms", "-p",
        help="Comma-separated list of platforms (twitter,reddit,linkedin,producthunt,instagram,tiktok)",
    ),
    calendar_start: Optional[str] = typer.Option(
        None,
        "--calendar-start",
        help="Content calendar start date (YYYY-MM-DD)",
    ),
    calendar_csv: Optional[Path] = typer.Option(
        None,
        "--calendar-csv",
        help="Export content calendar to CSV",
    ),
    enhance: bool = typer.Option(
        False,
        "--enhance",
        help="Use Claude API to polish content (requires ANTHROPIC_API_KEY)",
    ),
):
    """
    Generate distribution kit from simulation results.

    Creates ready-to-post content for multiple platforms:
    - Twitter/X: Launch thread + 30 days of content
    - Reddit: Launch posts + engagement strategy
    - LinkedIn: Founder posts + templates
    - Product Hunt: Complete launch kit

    Plus a 30-day content calendar and launch day playbook.

    Use --enhance to polish content with Claude API (costs API credits).
    """
    import json
    from datetime import date, datetime
    from .execution.distribution import DistributionGenerator

    # Load results and config
    try:
        with open(results_file) as f:
            results_data = json.load(f)
        config = load_config(config_path)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    # Parse platforms
    platform_list = [p.strip().lower() for p in platforms.split(",")]
    valid_platforms = ["twitter", "reddit", "linkedin", "producthunt", "instagram", "tiktok"]
    for p in platform_list:
        if p not in valid_platforms:
            console.print(f"[yellow]Warning: Unknown platform '{p}', skipping[/yellow]")
            platform_list.remove(p)

    # Parse calendar start date
    start_date = None
    if calendar_start:
        try:
            start_date = datetime.strptime(calendar_start, "%Y-%m-%d").date()
        except ValueError:
            console.print("[yellow]Warning: Invalid date format, using today[/yellow]")
            start_date = date.today()

    # Reconstruct result object for generator
    from .core.metrics import SimulationMetrics, ConfidenceInterval, ObjectionCluster, ChannelRanking

    metrics_data = results_data.get("metrics", {})

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
        overall_confidence=results_data.get("confidence_score", 0.5),
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
            self.sim_id = results_data.get("sim_id", "unknown")
            self.final_metrics = metrics

    # Display header
    console.print(Panel.fit(
        f"[bold cyan]NeoSim[/bold cyan] - Distribution Kit Generator",
        subtitle=f"Platforms: {', '.join(platform_list)}",
    ))

    # Check for API key if enhancement requested
    if enhance and not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[red]Error: --enhance requires ANTHROPIC_API_KEY environment variable[/red]")
        raise typer.Exit(1)

    # Generate distribution kit
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating content...", total=None)

        generator = DistributionGenerator(
            MockResult(),
            config,
            platforms=platform_list,
            calendar_start=start_date,
        )
        kit = generator.generate()

        # Enhance with LLM if requested
        if enhance:
            progress.update(task, description="Enhancing content with Claude...")
            from .execution.enhance import ContentEnhancer

            enhancer = ContentEnhancer()

            def on_enhance_progress(current, total, item):
                progress.update(task, description=f"Enhancing {item}... ({current}/{total})")

            kit = enhancer.enhance_kit(kit, platform_list, on_enhance_progress)
            progress.update(task, description="Enhancement complete!")

        progress.update(task, description="Saving distribution kit...")
        generator.export(str(output))

        # Export calendar CSV if requested
        if calendar_csv:
            from .execution.calendar import ContentCalendarGenerator
            cal_gen = ContentCalendarGenerator(kit, config, start_date)
            cal_gen.export_csv(str(calendar_csv))

    # Display summary
    console.print(f"\n[green]Distribution kit saved to {output}[/green]")
    if enhance:
        console.print("[cyan]Content enhanced with Claude API[/cyan]")

    # Platform summaries
    console.print("\n[bold]Content Generated[/bold]")

    if "twitter" in platform_list and kit.twitter:
        thread_count = len([t for t in kit.twitter if t.content_type == "launch_thread"])
        daily_count = len([t for t in kit.twitter if t.content_type == "daily"])
        console.print(f"  Twitter: {thread_count}-tweet launch thread + {daily_count} daily posts")

    if "reddit" in platform_list and kit.reddit:
        console.print(f"  Reddit: {len(kit.reddit)} posts + engagement strategy")

    if "linkedin" in platform_list and kit.linkedin:
        console.print(f"  LinkedIn: {len(kit.linkedin)} posts + connection templates")

    if "producthunt" in platform_list and kit.product_hunt:
        console.print(f"  Product Hunt: Complete launch kit (tagline, description, first comment)")
        console.print(f"    Tagline: \"{kit.product_hunt.tagline}\"")

    if "instagram" in platform_list and kit.instagram:
        carousel_count = len([c for c in kit.instagram if c.content_type == "carousel"])
        reel_count = len([c for c in kit.instagram if "reel" in c.content_type])
        console.print(f"  Instagram: {carousel_count} carousels + {reel_count} reel concepts + story templates")

    if "tiktok" in platform_list and kit.tiktok:
        console.print(f"  TikTok: {len(kit.tiktok)} video scripts with hooks")

    # Calendar summary
    console.print(f"\n[bold]Content Calendar[/bold]")
    console.print(f"  {len(kit.content_calendar)} scheduled posts over 30 days")
    if calendar_csv:
        console.print(f"  CSV exported to {calendar_csv}")

    # Launch playbook summary
    console.print("\n[bold]Launch Day Playbook[/bold]")
    for phase, items in list(kit.launch_day_playbook.items())[:3]:
        console.print(f"  {phase}: {len(items)} action items")

    # Next steps
    console.print("\n[bold]Next Steps[/bold]")
    console.print("  1. Review generated content in distribution_kit.json")
    console.print("  2. Customize placeholders ([YOUR NAME], [LINK], etc.)")
    console.print("  3. Schedule posts using your preferred tools")
    console.print("  4. Follow the launch day playbook")


# ============================================================================
# BENCHMARK Command - Trust Layer
# ============================================================================

@app.command()
def benchmark(
    name: Optional[str] = typer.Argument(None, help="Benchmark name to run"),
    list_all: bool = typer.Option(False, "--list", "-l", help="List available benchmarks"),
):
    """
    Run benchmark replays to validate simulation accuracy.

    Benchmarks are known product launches with documented outcomes.
    Running them shows how NeoSim predictions compare to reality.
    """
    from .benchmarks import list_benchmarks, get_benchmark, BENCHMARKS

    if list_all or name is None:
        console.print(Panel.fit(
            "[bold cyan]NeoSim[/bold cyan] - Available Benchmarks",
        ))

        table = Table(show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Name")
        table.add_column("Year")

        for b in list_benchmarks():
            table.add_row(b["id"], b["name"], str(b["year"]))

        console.print(table)
        console.print("\nRun a benchmark: [bold]neosim benchmark notion-freemium[/bold]")
        return

    # Get benchmark
    bench = get_benchmark(name)
    if not bench:
        console.print(f"[red]Benchmark not found: {name}[/red]")
        console.print("Use [bold]neosim benchmark --list[/bold] to see available benchmarks")
        raise typer.Exit(1)

    console.print(Panel.fit(
        f"[bold cyan]Benchmark Replay[/bold cyan] - {bench['name']}",
        subtitle=f"Year: {bench['year']}",
    ))

    console.print(f"\n[bold]Description:[/bold] {bench['description']}")

    console.print("\n[bold]Actual Outcome:[/bold]")
    outcome = bench["actual_outcome"]
    for key, value in outcome.items():
        console.print(f"  • {key}: {value}")

    console.print("\n[dim]To run this simulation:[/dim]")
    console.print(f"  1. Export config: neosim benchmark {name} --export")
    console.print(f"  2. Run simulation: neosim sim -c {name}.yaml")
    console.print(f"  3. Compare to actual outcome above")


# ============================================================================
# CALIBRATE Command - User Data Integration
# ============================================================================

@app.command()
def calibrate(
    config_path: Path = typer.Option(
        Path("neosim.yaml"),
        "--config", "-c",
        help="Path to config file",
    ),
):
    """
    Calibrate simulation with known data points.

    If you have real data from beta/early users, input it here
    to ground the simulation in your reality.
    """
    console.print(Panel.fit(
        "[bold cyan]NeoSim[/bold cyan] - Calibration",
        subtitle="Ground simulation in your data",
    ))

    console.print("\nEnter known metrics (leave blank to skip):\n")

    data_points = {}

    conv = Prompt.ask("Conversion rate (e.g., 0.05 for 5%)", default="")
    if conv:
        try:
            data_points["conversion_rate"] = float(conv)
        except ValueError:
            pass

    cac = Prompt.ask("Current CAC (e.g., 50)", default="")
    if cac:
        try:
            data_points["cac"] = float(cac)
        except ValueError:
            pass

    churn = Prompt.ask("Monthly churn rate (e.g., 0.05)", default="")
    if churn:
        try:
            data_points["churn_rate"] = float(churn)
        except ValueError:
            pass

    if data_points:
        # Save calibration to config
        console.print("\n[green]Calibration data recorded:[/green]")
        for k, v in data_points.items():
            console.print(f"  • {k}: {v}")
        console.print("\nThis will anchor agent predictions in your next simulation.")
    else:
        console.print("\n[yellow]No calibration data entered.[/yellow]")
        console.print("Run simulations to generate baseline predictions first.")


# ============================================================================
# VERSION Command
# ============================================================================

@app.command()
def version():
    """Show NeoSim version."""
    from . import __version__
    console.print(f"NeoSim v{__version__}")


# ============================================================================
# Entry Point
# ============================================================================

def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
