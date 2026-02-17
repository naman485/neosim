# NeoSim

> **The Staging Environment for Distribution**

You wouldn't push code to production without staging. Why would you push your GTM?

NeoSim is a CLI-first simulation engine that lets founders stress-test their Go-To-Market strategy before spending a dollar on execution.

## Quick Start

```bash
# Install
pip install neosim

# Or install from source
pip install -e .

# Set your API key (choose one based on your provider)
export ANTHROPIC_API_KEY=sk-ant-...  # Claude
# OR
export OPENAI_API_KEY=sk-...         # GPT-4
# OR
export GROQ_API_KEY=gsk_...          # Groq (fast inference)
# OR run locally with Ollama (no key needed)

# Initialize project
neosim init

# Run simulation
neosim sim
```

## What It Does

NeoSim deploys LLM-powered agents to simulate:

- **Buyer Agents** - ICP personas making buy/pass/object decisions
- **Competitor Agents** - Predicting competitive responses
- **Channel Agents** - Projecting CAC, reach, and ROI per channel
- **Advisor Agent** - Synthesizing insights and flagging risks

Each simulation produces:
- Projected metrics with confidence intervals (CAC, conversion, time-to-breakeven)
- Top buyer objections with suggested counters
- Channel rankings by expected ROI
- Competitive risk assessment
- Strategic recommendations

## Commands

```bash
neosim init              # Interactive project setup
neosim sim               # Run GTM simulation
neosim sim -n 30         # Run with 30 cycles
neosim compare a.yaml b.yaml  # A/B test strategies
neosim report results.json    # Generate shareable HTML report
neosim execute results.json   # Generate execution plan
neosim distribute results.json # Generate platform-ready content
```

## Configuration

NeoSim is configured via `neosim.yaml`:

```yaml
version: "1.0"
project_name: "My Startup"

# LLM Configuration - choose your provider
llm_provider: "anthropic"  # anthropic, openai, google, groq, together, ollama
llm_model: "claude-sonnet-4-20250514"

product:
  name: "AwesomeApp"
  description: "AI-powered productivity tool"
  category: "SaaS"
  stage: "pre-launch"
  unique_value_prop: "10x faster with AI assistance"

icp_personas:
  - name: "Technical Founder"
    role: "Founder/CTO"
    company_size: "startup"
    pain_points:
      - "Manual repetitive tasks"
      - "Scaling bottlenecks"
    goals:
      - "Ship faster"
      - "Reduce ops overhead"

pricing:
  model: "freemium"
  tiers:
    - name: "Free"
      price: 0
    - name: "Pro"
      price: 29

channels:
  - name: "organic-social"
    priority: 5
  - name: "community"
    priority: 4

competitors:
  - name: "BigCorp"
    positioning: "Enterprise solution"
    market_share: "dominant"

simulation:
  cycles: 30
  buyer_agents: 20
```

## Output Example

```
╭──────────────────────────────────────────────────────────────╮
│ NeoSim - Simulation Complete                                 │
│ ID: a1b2c3d4 | Duration: 45.2s                              │
╰──────────────────────────────────────────────────────────────╯

Overall Assessment: PROMISING
Confidence Score: 72%

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━┓
┃ Metric             ┃ Low    ┃ Mid    ┃ High   ┃ Confidence ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━┩
│ CAC                │ $32    │ $48    │ $71    │ medium     │
│ Conversion Rate    │ 4.2%   │ 6.8%   │ 9.1%   │ medium     │
│ Time to Breakeven  │ 3mo    │ 5mo    │ 8mo    │ low        │
└────────────────────┴────────┴────────┴────────┴────────────┘

Top Objections:
  - Price (12x): Emphasize ROI and time savings
  - Trust (8x): Lead with social proof and case studies

Channel Rankings:
  1. community: Score 8.2 (ROI 3.1x at $28 CAC)
  2. organic-social: Score 6.5 (ROI 2.4x at $42 CAC)

Strategic Recommendations:
  - Focus on community-led growth before paid acquisition
  - Address pricing objections with clear ROI calculator
  - Build trust through beta user case studies
```

## Distribution Bridge

After running a simulation, use the Distribution Bridge to generate **ready-to-post content** for your launch:

```bash
# Generate full distribution kit
neosim distribute results.json

# Output: distribution_kit.json
```

### What It Generates

| Platform | Content |
|----------|---------|
| **Twitter/X** | 8-tweet launch thread + 30 days of daily content + engagement hooks |
| **Reddit** | Launch post (Show & Tell format) + value posts + comment strategy |
| **LinkedIn** | Founder journey posts + thought leadership + connection templates |
| **Product Hunt** | Tagline, description, first comment, media checklist, hunter outreach |
| **Instagram** | Carousel posts + Reel concepts with scripts + Story templates + bio optimization |
| **TikTok** | Video hooks (first 3 sec) + full scripts + trend adaptations + format templates |

Plus:
- **30-day content calendar** with optimal posting times
- **Launch day playbook** (T-24h → first 24h action items)
- **Engagement templates** for replies and objection handling

### Usage Options

```bash
# Full distribution kit (text platforms)
neosim distribute results.json

# Include video platforms (Instagram + TikTok)
neosim distribute results.json --platforms twitter,reddit,linkedin,producthunt,instagram,tiktok

# Specific platforms only
neosim distribute results.json --platforms twitter,producthunt

# Custom output location
neosim distribute results.json -o my_launch_kit.json

# Set calendar start date
neosim distribute results.json --calendar-start 2024-03-15

# Export calendar to CSV (for import to scheduling tools)
neosim distribute results.json --calendar-csv calendar.csv

# Polish content with Claude API (costs API credits)
neosim distribute results.json --enhance
```

### Output Structure

```json
{
  "metadata": {
    "simulation_id": "a1b2c3d4",
    "product_name": "MyApp",
    "generated_at": "2024-02-15T10:00:00Z"
  },
  "platforms": {
    "twitter": {
      "launch_thread": ["Tweet 1...", "Tweet 2..."],
      "daily_content": [...],
      "engagement_hooks": [...]
    },
    "reddit": {
      "posts": [...],
    },
    "linkedin": {
      "posts": [...]
    },
    "product_hunt": {
      "tagline": "60 char tagline",
      "description": "260 char description",
      "first_comment": "Maker story..."
    }
  },
  "content_calendar": [
    {"day": 1, "platform": "producthunt", "time": "12:01am PST", "priority": "critical"},
    {"day": 1, "platform": "twitter", "time": "6:00am EST", "priority": "critical"}
  ],
  "launch_playbook": {
    "t_minus_24h": ["Warm up audience..."],
    "launch_hour": ["Post PH", "Tweet thread"],
    "first_24h": ["Reply to all comments"]
  }
}
```

### Workflow

```
1. neosim init          → Create config
2. neosim sim -o results.json   → Run simulation
3. neosim distribute results.json → Generate content
4. Review & customize   → Replace [PLACEHOLDERS]
5. Schedule & launch    → Use your favorite tools
```

## LLM Providers

NeoSim is **LLM-agnostic** - choose the provider that fits your needs:

| Provider | Env Variable | Default Model | Notes |
|----------|--------------|---------------|-------|
| `anthropic` | `ANTHROPIC_API_KEY` | claude-sonnet-4-20250514 | Recommended for quality |
| `openai` | `OPENAI_API_KEY` | gpt-4o | GPT-4 family |
| `google` | `GOOGLE_API_KEY` | gemini-1.5-pro | Gemini models |
| `groq` | `GROQ_API_KEY` | llama-3.3-70b-versatile | Fast inference |
| `together` | `TOGETHER_API_KEY` | Llama-3.3-70B-Instruct | Open models |
| `ollama` | *(none - local)* | llama3.2 | Run locally, free |

Set your provider in `neosim.yaml`:

```yaml
llm_provider: "groq"  # Fast and cheap
llm_model: "llama-3.3-70b-versatile"
```

Then set the corresponding API key:

```bash
export GROQ_API_KEY=gsk_...
```

For Ollama (local), just ensure Ollama is running - no API key needed.

## Development

```bash
# Clone
git clone https://github.com/nodeops/neosim
cd neosim

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format
black neosim/
ruff check neosim/
```

## Roadmap

- [x] CLI scaffold, config schema, agent prompts
- [x] Simulation engine, Rich terminal output
- [x] HTML reports, benchmark replays
- [x] A/B compare mode, JSON export
- [x] **Distribution Bridge** - Platform content generation
  - [x] Twitter/X generator (threads + daily content)
  - [x] Reddit generator (launch posts + strategy)
  - [x] LinkedIn generator (founder posts + templates)
  - [x] Product Hunt generator (complete launch kit)
  - [x] Instagram generator (carousels + reels + stories)
  - [x] TikTok generator (hooks + scripts + trends)
  - [x] 30-day content calendar
  - [x] Launch day playbook
  - [x] LLM content enhancement (`--enhance` flag)
- [x] **Multi-LLM Support** - Provider agnostic
  - [x] Anthropic (Claude)
  - [x] OpenAI (GPT-4)
  - [x] Google (Gemini)
  - [x] Groq (fast inference)
  - [x] Together AI (open models)
  - [x] Ollama (local/free)
- [x] Lifetime pricing model
- [ ] CreateOS integration
- [ ] Beta launch

## License

MIT
