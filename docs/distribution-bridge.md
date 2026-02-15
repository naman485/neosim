# Distribution Bridge

> Generate ready-to-post content for your product launch across Twitter, Reddit, LinkedIn, and Product Hunt.

The Distribution Bridge converts NeoSim simulation insights into **platform-native content** you can actually post. No more staring at a blank page wondering what to write.

## Quick Start

```bash
# 1. Run a simulation first
neosim sim -o results.json

# 2. Generate distribution kit
neosim distribute results.json

# 3. Review output
cat distribution_kit.json
```

That's it. You now have:
- An 8-tweet launch thread
- 30 days of Twitter content
- Reddit launch posts with engagement rules
- LinkedIn founder posts
- A complete Product Hunt launch kit
- A 30-day content calendar
- A launch day playbook

---

## Command Reference

```bash
neosim distribute <results_file> [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `results_file` | Path to simulation results JSON (from `neosim sim -o`) |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `-c, --config` | `neosim.yaml` | Path to NeoSim config file |
| `-o, --output` | `distribution_kit.json` | Output file path |
| `-p, --platforms` | `twitter,reddit,linkedin,producthunt` | Comma-separated platforms |
| `--calendar-start` | Today | Content calendar start date (YYYY-MM-DD) |
| `--calendar-csv` | None | Export calendar to CSV file |

### Examples

```bash
# All platforms, default output
neosim distribute results.json

# Twitter and Product Hunt only
neosim distribute results.json -p twitter,producthunt

# Custom config and output
neosim distribute results.json -c my_config.yaml -o launch_kit.json

# Set launch date for calendar
neosim distribute results.json --calendar-start 2024-04-01

# Export calendar for scheduling tools
neosim distribute results.json --calendar-csv calendar.csv
```

---

## Platform Content

### Twitter/X

The Twitter generator creates:

#### Launch Thread (8 tweets)
A complete narrative thread for launch day:
1. Hook + announcement
2. The problem you're solving
3. Why existing solutions fail
4. Your solution introduction
5. Key features (part 1)
6. Key features (part 2)
7. Pricing/accessibility
8. CTA + request for support

#### Daily Content (30 posts)
Rotating content types:
- **Tips** - Actionable advice related to your product
- **Problem** - Highlight pain points you solve
- **Feature** - Spotlight specific features
- **Social proof** - User wins and testimonials
- **Behind the scenes** - Building in public content

#### Engagement Hooks (5 posts)
Questions and conversation starters to drive engagement.

**Character limits respected:** All content fits within 280 characters.

---

### Reddit

The Reddit generator creates:

#### Launch Post
Authentic, value-first post following Reddit conventions:
- No marketing speak
- Genuine backstory
- Clear what/why/how
- Explicit ask for feedback
- Appropriate for r/startups Show & Tell format

#### Value Posts
Educational posts that provide value first:
- "How we solved X" lessons
- AMA-style engagement
- Technical deep-dives (for DevTools)

#### Comment Strategy
A complete guide for engaging on Reddit:
- Subreddit-specific behavior rules
- Response templates
- Subreddits to monitor
- Do's and don'ts

**Subreddit targeting:** Automatically suggests relevant subreddits based on your product category.

---

### LinkedIn

The LinkedIn generator creates:

#### Launch Announcement
Founder-voice personal post with:
- Strong opening hook
- Journey narrative
- Feature bullets
- Clear CTA

#### Journey Posts
Authentic founder content:
- "The struggle" post
- "Lessons learned" post
- "The pivot" post

#### Thought Leadership
Industry insight posts:
- Market observations
- Predictions
- Controversial takes

#### Connection Templates
Outreach messages:
- Connection request
- Post-connection follow-up
- Soft product introduction

---

### Product Hunt

The Product Hunt generator creates a complete launch kit:

#### Core Assets
- **Tagline** (60 chars max) - Punchy one-liner
- **Description** (260 chars max) - Compelling summary
- **First Comment** - Your maker story (crucial for success)

#### Supporting Materials
- **Topics** - Relevant PH categories
- **Media Checklist** - All assets you need to prepare
- **Hunter Outreach Template** - Email for reaching out to hunters
- **Launch Day Prep** - Hour-by-hour checklist

---

## Content Calendar

The 30-day calendar coordinates content across platforms:

### Structure

| Phase | Days | Intensity | Focus |
|-------|------|-----------|-------|
| Launch Day | 1 | Critical | All platforms go live |
| Launch Week | 2-7 | High | Momentum building |
| Week Two | 8-14 | Moderate | Sustained engagement |
| Sustain | 15-30 | Regular | Consistent presence |

### Calendar Entry Format

```json
{
  "day": 1,
  "date": "2024-03-15",
  "platform": "producthunt",
  "content_type": "launch",
  "preview": "First 100 chars of content...",
  "time": "12:01am PST",
  "priority": "critical",
  "notes": "Go live! Post maker comment immediately."
}
```

### Optimal Posting Times

| Platform | Best Times | Best Days |
|----------|------------|-----------|
| Twitter | 9am, 12pm, 5pm EST | Tue, Wed, Thu |
| Reddit | 10am, 2pm EST | Mon, Tue, Sat |
| LinkedIn | 8am, 12pm local | Tue, Wed, Thu |
| Product Hunt | 12:01am PST | Tue, Wed, Thu |

### Export Options

```bash
# JSON (default)
neosim distribute results.json -o kit.json

# CSV (for Google Sheets, Notion, scheduling tools)
neosim distribute results.json --calendar-csv calendar.csv
```

---

## Launch Day Playbook

The playbook provides hour-by-hour guidance:

### T-24 Hours
- Warm up audience with teaser content
- Notify beta users about upcoming launch
- Prepare all assets and links
- Test all landing page CTAs
- Queue social posts for optimal times

### T-1 Hour
- Final check: PH listing ready
- Notify hunter (if using one)
- Have team ready to engage
- Open all social platforms

### Launch Hour
- Post on Product Hunt (12:01am PST)
- Post Twitter launch thread immediately after
- Post LinkedIn announcement
- Share in relevant communities
- Reply to first PH comment yourself

### First 4 Hours
- Respond to EVERY Product Hunt comment
- Engage with all Twitter replies
- DM supporters thanking them
- Share behind-the-scenes content

### First 24 Hours
- Continue responding to all engagement
- Post follow-up content on each platform
- Email your list with launch news
- Reach out to journalists/bloggers
- Track metrics and adjust messaging

---

## Engagement Templates

Pre-written responses for common situations:

### Thank You Responses
```
Thanks so much for the support! Really means a lot.
Appreciate you checking out [Product]!
Thank you! Let me know if you have any questions.
```

### Question Responses
```
Great question! {answer}
Absolutely - {answer}
{answer} - let me know if that helps!
```

### Objection Handling
Uses your simulation's top objections with suggested counters:
```
Objection: "Seems expensive"
Response: "I hear you! Here's how we think about pricing..."
```

---

## Customization

All generated content includes placeholders you should customize:

| Placeholder | Replace With |
|-------------|--------------|
| `[YOUR NAME]` | Your actual name |
| `[LINK]` | Your product URL |
| `[X]` | Specific numbers (users, MRR, etc.) |
| `[COMPANY]` | Specific company names |
| `[INSERT TESTIMONIAL]` | Real user quotes |
| `[UPCOMING FEATURE 1]` | Your roadmap items |

### Tips for Customization

1. **Keep the structure** - The format is optimized for each platform
2. **Add real numbers** - Replace [X] with actual metrics
3. **Insert testimonials** - Real quotes beat placeholder text
4. **Adjust voice** - Match your personal writing style
5. **Add specifics** - Generic content performs worse

---

## Integration with Other Tools

### Scheduling Tools
Export the calendar and import into:
- Buffer
- Hootsuite
- Later
- Typefully (Twitter)
- Publer

```bash
neosim distribute results.json --calendar-csv calendar.csv
# Import calendar.csv into your scheduling tool
```

### Notion
1. Export as CSV
2. Import into Notion database
3. Add status columns, assignees

### Google Sheets
1. Export as CSV
2. Import into Sheets
3. Add conditional formatting for priority
4. Share with team

---

## Best Practices

### Before Launch

1. **Review all content** - Don't post blindly
2. **Replace all placeholders** - Search for `[` to find them
3. **Test all links** - Broken links kill conversions
4. **Prepare assets** - Have images ready for all platforms
5. **Brief your team** - Everyone should know the plan

### Launch Day

1. **Follow the playbook** - It's hour-by-hour for a reason
2. **Respond to everything** - Engagement begets engagement
3. **Stay online** - Don't launch and disappear
4. **Track metrics** - Know what's working
5. **Adapt messaging** - If something resonates, double down

### Post-Launch

1. **Stick to the calendar** - Consistency beats intensity
2. **Repurpose what works** - Turn tweets into LinkedIn posts
3. **Engage authentically** - Don't automate replies
4. **Measure and iterate** - Learn from each post

---

## Troubleshooting

### "No simulation results found"
Make sure you ran a simulation first:
```bash
neosim sim -o results.json
neosim distribute results.json
```

### "Content seems generic"
The generator uses your `neosim.yaml` config. More detailed config = better content:
- Add more pain points
- Add specific features
- Add competitor details
- Add ICP details

### "Wrong platform focus"
Use the `--platforms` flag to generate only what you need:
```bash
neosim distribute results.json -p twitter,producthunt
```

---

## Architecture

```
SimulationResult + Config
         ↓
┌─────────────────────────────────────────┐
│        DistributionGenerator            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ Twitter │ │ Reddit  │ │LinkedIn │   │
│  │Generator│ │Generator│ │Generator│   │
│  └─────────┘ └─────────┘ └─────────┘   │
│  ┌─────────┐                           │
│  │ProductH.│                           │
│  │Generator│                           │
│  └─────────┘                           │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│         ContentCalendarGenerator         │
│  30-day cross-platform posting schedule  │
└─────────────────────────────────────────┘
         ↓
    distribution_kit.json
```

### Files

| File | Purpose |
|------|---------|
| `execution/distribution.py` | DistributionKit + DistributionGenerator |
| `execution/calendar.py` | ContentCalendarGenerator |
| `execution/platforms/base.py` | BasePlatformGenerator |
| `execution/platforms/twitter.py` | TwitterGenerator |
| `execution/platforms/reddit.py` | RedditGenerator |
| `execution/platforms/linkedin.py` | LinkedInGenerator |
| `execution/platforms/producthunt.py` | ProductHuntGenerator |

---

---

## Instagram

The Instagram generator creates content optimized for visual engagement:

### Carousels
- **Launch carousel** - Announce your product with swipeable slides
- **Educational carousels** - How-to guides, tips, myth-busting
- **Pain point carousels** - "Signs you need [product]"

### Reel Concepts
Complete video concepts with:
- **Hook (0-3s)** - Critical opening to stop the scroll
- **Script** - Full timestamped script
- **Format template** - POV, tutorial, day-in-life, etc.

Formats include:
- Hook + Tutorial
- Day in the life
- POV reactions
- Talking head educational

### Stories
- Launch day sequence
- Engagement templates (polls, questions)
- Feature highlights

### Bio Optimization
Multiple bio options optimized for conversion.

---

## TikTok

The TikTok generator focuses on the critical first 3 seconds:

### Video Hooks
Proven hook templates:
- "Stop scrolling if you..."
- "Nobody talks about this but..."
- "POV: You just discovered..."
- "The secret to [X]..."

### Full Scripts
Timestamped scripts including:
- Hook (0-3s)
- Context/Problem (3-10s)
- Solution/Demo (10-25s)
- CTA (25-30s)

### Trend Adaptations
- POV format
- Day in the life
- Duet/Stitch reactions
- Trending sound adaptations

### Content Types
- Launch announcement
- Tutorials
- Hot takes
- Tips format
- Founder storytime

---

## LLM Enhancement

Use `--enhance` to polish content with Claude API:

```bash
neosim distribute results.json --enhance
```

### What It Does
- Improves clarity and engagement
- Strengthens hooks and CTAs
- Makes content more natural
- Maintains platform constraints (char limits)

### Requirements
- `ANTHROPIC_API_KEY` environment variable
- Uses Claude API (costs API credits)

### What Gets Enhanced
- Twitter tweets and threads
- Reddit post titles and bodies
- LinkedIn post text and hooks
- Product Hunt tagline, description, first comment

---

## Future Plans

- [ ] Direct scheduling integration
- [ ] A/B content variants
- [ ] Analytics feedback loop
- [ ] Video thumbnail suggestions
