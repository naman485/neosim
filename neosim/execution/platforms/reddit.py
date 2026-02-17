"""
Reddit Content Generator

Generates:
- Launch posts (authentic, value-first)
- Value posts for sustained engagement
- Comment strategy and rules
- Karma-building strategy

Platform Best Practices (2024):
- AUTHENTICITY IS EVERYTHING (Redditors detect marketing instantly)
- NO self-promotion until you have karma and history
- Value-first: Give 10x before asking for anything
- Each subreddit has DIFFERENT rules - read them
- Title is 80% of success
- Best times: US morning weekdays (9-11am EST)
- Respond to every comment (builds trust)
- Use "I" not "we" (personal voice wins)
- Flair requirements vary by subreddit
- Karma threshold: 100+ comment karma before posting in most subs
"""

from typing import List
from .base import BasePlatformGenerator
from ..distribution import RedditContent


class RedditGenerator(BasePlatformGenerator):
    """Generate Reddit content following community best practices."""

    # Reddit-specific settings
    MAX_TITLE_LENGTH = 300
    MAX_POST_LENGTH = 40000  # Self-posts

    # Optimal posting times (US-centric, most traffic)
    OPTIMAL_TIMES = ["9:00am EST", "10:00am EST", "2:00pm EST"]
    BEST_DAYS = ["monday", "tuesday", "wednesday", "saturday"]

    # Subreddit targeting by category with rules
    SUBREDDIT_MAP = {
        "SaaS": ["SaaS", "startups", "Entrepreneur", "smallbusiness", "indiehackers"],
        "DevTool": ["programming", "webdev", "devops", "SideProject", "coolgithubprojects"],
        "Consumer": ["ProductManagement", "startups", "Entrepreneur"],
        "Marketplace": ["startups", "Entrepreneur", "smallbusiness"],
        "API": ["programming", "webdev", "devops", "coding"],
    }

    # Detailed subreddit rules (these are CRITICAL)
    SUBREDDIT_RULES = {
        "startups": {
            "rules": [
                "Use 'Show & Tell' or 'SaaS' flair ONLY",
                "Self-post required (no direct links)",
                "Include: problem, solution, traction, ask",
                "NO asking for upvotes",
                "Respond to every comment",
            ],
            "karma_required": 0,
            "self_promo_allowed": True,
            "format": "show_and_tell",
        },
        "SaaS": {
            "rules": [
                "Tag post with [Tool] or relevant flair",
                "Include pricing transparency",
                "Share real metrics if possible",
                "Self-promotion OK in designated threads",
            ],
            "karma_required": 10,
            "self_promo_allowed": True,
            "format": "standard",
        },
        "indiehackers": {
            "rules": [
                "Share your journey, not just the product",
                "Include revenue/metrics if comfortable",
                "Be authentic about struggles",
                "Cross-posting from indiehackers.com welcome",
            ],
            "karma_required": 0,
            "self_promo_allowed": True,
            "format": "journey",
        },
        "programming": {
            "rules": [
                "NO self-promotion (will get removed)",
                "Technical content only",
                "Code examples required for discussions",
                "Read sidebar rules carefully",
            ],
            "karma_required": 100,
            "self_promo_allowed": False,
            "format": "technical",
        },
        "webdev": {
            "rules": [
                "Self-promo only in Showoff Saturday thread",
                "Technical discussions welcome anytime",
                "Include tech stack details",
            ],
            "karma_required": 50,
            "self_promo_allowed": "saturday_only",
            "format": "technical",
        },
    }

    def generate(self) -> List[RedditContent]:
        """Generate all Reddit content with karma-building strategy."""
        content = []

        # FIRST: Karma-building strategy (do this BEFORE launch posts)
        content.append(self._generate_karma_strategy())

        # Primary launch post
        content.append(self._generate_launch_post())

        # Value posts for different subreddits
        content.extend(self._generate_value_posts())

        # Comment strategy
        content.append(self._generate_comment_strategy())

        return content

    def _generate_karma_strategy(self) -> RedditContent:
        """
        Generate karma-building strategy.

        CRITICAL: You need karma before most subreddits will let you post.
        This strategy should be followed 2-4 weeks before launch.
        """
        ctx = self.context
        subreddits = self._get_target_subreddits()

        body = f"""## Karma-Building Strategy for {ctx.product_name} Launch

**Timeline:** Start 2-4 weeks before planned launch

**Goal:** Build 100+ comment karma and establish presence in target communities

---

### Phase 1: Lurk and Learn (Week 1)
- Subscribe to: {', '.join(['r/' + s for s in subreddits])}
- Read top posts from past month in each subreddit
- Note the tone, style, and what gets upvoted
- Identify common questions you can answer

### Phase 2: Add Value (Weeks 2-3)
- Comment on 3-5 posts per day (genuinely helpful comments)
- Answer questions in your area of expertise
- Share insights WITHOUT mentioning your product
- Upvote good content (builds goodwill)

**Comment templates that work:**

1. **Helpful answer:**
   "I dealt with this exact problem. Here's what worked for me: [specific advice]. Hope that helps!"

2. **Add to discussion:**
   "Great point. I'd also add that [relevant insight from your experience]."

3. **Ask clarifying question:**
   "Interesting approach! How did you handle [specific challenge]?"

### Phase 3: Light Engagement (Week 4)
- Start a few discussion posts (not about your product)
- Share useful resources you've found
- Build recognition by being consistently helpful

### Red Flags to Avoid
❌ Don't mention your product until you have karma
❌ Don't post links to your site in comments
❌ Don't use multiple accounts (instant ban)
❌ Don't ask for upvotes ever
❌ Don't copy-paste the same comment

### Subreddit-Specific Rules

{self._format_subreddit_rules()}

---

**Remember:** Redditors can smell marketing from a mile away. Be genuine, be helpful, be patient.
"""

        return RedditContent(
            content_type="karma_strategy",
            title="Pre-Launch Karma Building Strategy",
            body=body.strip(),
            target_subreddits=[],
            engagement_rules=[
                "Start 2-4 weeks before launch",
                "Comment genuinely on 3-5 posts daily",
                "Never mention your product while building karma",
                "Read and follow each subreddit's rules",
            ],
        )

    def _format_subreddit_rules(self) -> str:
        """Format subreddit-specific rules."""
        lines = []
        for sub, rules in self.SUBREDDIT_RULES.items():
            if sub in self._get_target_subreddits():
                lines.append(f"\n**r/{sub}:**")
                for rule in rules.get("rules", []):
                    lines.append(f"  - {rule}")
                if rules.get("karma_required", 0) > 0:
                    lines.append(f"  - Karma required: {rules['karma_required']}+")
                if rules.get("self_promo_allowed") == False:
                    lines.append(f"  - ⚠️ NO self-promotion allowed")
                elif rules.get("self_promo_allowed") == "saturday_only":
                    lines.append(f"  - Self-promo: Saturday threads only")
        return "\n".join(lines)

    def _generate_launch_post(self) -> RedditContent:
        """Generate main launch post."""
        ctx = self.context

        # Reddit-style authentic title
        title = f"After [X] months of building, I finally launched {ctx.product_name} - {ctx.product_description}"
        title = self.truncate(title, self.MAX_TITLE_LENGTH)

        # Body follows Reddit conventions: authentic, detailed, value-first
        body = f"""Hey r/startups,

Long-time lurker, first-time poster for a launch.

**TL;DR:** Built {ctx.product_name} to solve {ctx.pain_points[0].lower() if ctx.pain_points else 'a problem'} for {ctx.target_roles[0].lower() if ctx.target_roles else 'people'}s. It's finally live.

---

**The backstory:**

Like many of you, I was frustrated with {ctx.pain_points[0].lower() if ctx.pain_points else 'the existing solutions'}. Every tool I tried was either:
- Too complex for what I needed
- Too expensive for a small team
- Built for enterprises, not actual users

So I built {ctx.product_name}.

**What it does:**

{ctx.unique_value_prop}

Key features:
{self._format_features()}

**Pricing:**

{self._format_pricing()}

**What I learned building this:**

1. Talk to users early and often
2. Simple beats feature-rich
3. Launch before you're ready (you'll never feel ready)

---

Would love to hear your thoughts - what am I missing? What would make this more useful for you?

Happy to answer any questions about the product, tech stack, or journey.

[LINK]

---

*Edit: Wow, didn't expect this response! Trying to reply to everyone.*
"""

        subreddits = self._get_target_subreddits()

        return RedditContent(
            content_type="launch_post",
            title=title,
            body=body.strip(),
            target_subreddits=subreddits,
            flair="Show & Tell" if "startups" in subreddits else None,
            engagement_rules=[
                "Respond to every comment within 2 hours",
                "Thank critics for feedback (don't get defensive)",
                "Add edits to acknowledge popular questions",
                "Upvote helpful comments from others",
                "Never argue with trolls",
            ],
        )

    def _generate_value_posts(self) -> List[RedditContent]:
        """Generate value-first posts for different subreddits."""
        ctx = self.context
        posts = []

        # Educational post - how we solved X
        posts.append(RedditContent(
            content_type="value_post",
            title=f"How we reduced {ctx.pain_points[0].lower() if ctx.pain_points else 'complexity'} by 80% - lessons learned",
            body=f"""Hey everyone,

Wanted to share some lessons from building {ctx.product_name}. Not trying to promote - just thought these insights might help others.

**The challenge:**

{ctx.pain_points[0] if ctx.pain_points else 'Building something users actually want'} is harder than it looks. We tried 3 different approaches before finding one that worked.

**What we learned:**

1. **Start with the workflow, not the feature.** We mapped out exactly how {ctx.target_roles[0].lower() if ctx.target_roles else 'our users'}s work before writing code.

2. **Simplify ruthlessly.** Our first version had 10 features. The version that worked has 3.

3. **Get feedback before building.** Sounds obvious, but we wasted weeks building things nobody wanted.

**Results:**

Users now complete the workflow in [X] minutes instead of [Y] hours.

---

What strategies have worked for you when solving complex problems?

*(If anyone's curious about the tool itself, it's in my profile - but this post is about the process, not the product)*
""",
            target_subreddits=["startups", "Entrepreneur"],
            engagement_rules=["Focus on helping, not selling"],
        ))

        # AMA-style post
        posts.append(RedditContent(
            content_type="value_post",
            title=f"I'm building a {ctx.category.lower()} product as a solo founder - AMA about the journey",
            body=f"""Hey r/startups,

Building {ctx.product_name} solo for the past [X] months. Happy to answer questions about:

- The tech stack decisions
- Finding first users
- Pricing strategy
- The emotional rollercoaster of solo founding
- Mistakes I've made (many)

A bit of context:
- {ctx.product_description}
- Currently at [X] users / [X] MRR
- Bootstrapped, no funding

Fire away!
""",
            target_subreddits=["startups", "indiehackers"],
        ))

        # Technical deep-dive (if DevTool)
        if ctx.category == "DevTool":
            posts.append(RedditContent(
                content_type="value_post",
                title=f"Building a {ctx.product_description.lower()} - architecture decisions and trade-offs",
                body=f"""Working on {ctx.product_name} and wanted to share some technical decisions we made.

**The problem:**
{ctx.pain_points[0] if ctx.pain_points else 'Scaling while keeping things simple'}

**Our approach:**

[SHARE TECHNICAL DETAILS]

**Trade-offs:**

- Chose simplicity over flexibility
- Optimized for the 80% use case
- [MORE TRADE-OFFS]

**Would love feedback:**
- Are we missing something obvious?
- How would you approach this differently?

Code is open source: [LINK IF APPLICABLE]
""",
                target_subreddits=["programming", "webdev"],
            ))

        return posts

    def _generate_comment_strategy(self) -> RedditContent:
        """Generate comment strategy guide."""
        ctx = self.context

        return RedditContent(
            content_type="comment_strategy",
            title="Comment Engagement Strategy",
            body=f"""## Reddit Comment Strategy for {ctx.product_name}

### Rules of Engagement

1. **Be helpful first, promote second (or never)**
   - Answer questions thoroughly
   - Share relevant insights
   - Only mention {ctx.product_name} if directly relevant

2. **Subreddit-specific behavior:**
   - r/startups: Be humble, share journey
   - r/SaaS: Focus on metrics, pricing transparency
   - r/programming: Technical depth, no marketing speak

3. **Comment templates:**

**When someone mentions a problem you solve:**
```
I've dealt with this too. A few things that helped:
1. [Actionable tip]
2. [Actionable tip]
3. [Actionable tip]

Also built a tool for this if you want to check it out: [product name]. But the above should help regardless.
```

**When asked directly about your product:**
```
Happy to share! We built {ctx.product_name} to [solve problem].

Key difference from alternatives: [unique value]

Pricing: [transparent pricing]

Would love your feedback if you try it.
```

**Handling criticism:**
```
That's fair feedback - appreciate you being direct.

[Address specific concern]

We're working on [improvement]. Would love to hear more about what would make it useful for you.
```

### Subreddits to Monitor

{self._format_subreddit_monitor_list()}
""",
            target_subreddits=[],
            engagement_rules=[
                "Check relevant subreddits daily",
                "Respond within 2 hours during launch week",
                "Never be defensive",
                "Upvote genuinely helpful comments",
            ],
        )

    def _get_target_subreddits(self) -> List[str]:
        """Get target subreddits based on category."""
        category = self.context.category
        return self.SUBREDDIT_MAP.get(category, ["startups", "Entrepreneur"])

    def _format_features(self) -> str:
        """Format features for Reddit post."""
        features = self.context.key_features[:4] if self.context.key_features else ["Easy to use"]
        return "\n".join([f"- {f}" for f in features])

    def _format_pricing(self) -> str:
        """Format pricing info."""
        ctx = self.context
        if ctx.pricing_model == "freemium":
            return "Free tier available. Paid plans start at $X/mo."
        elif ctx.pricing_model == "free-trial":
            return "14-day free trial, no credit card required. Plans from $X/mo."
        else:
            tiers = ctx.pricing_tiers
            if tiers:
                return f"Starting at ${tiers[0]['price']}/mo"
            return "Contact for pricing"

    def _format_subreddit_monitor_list(self) -> str:
        """Format subreddit monitoring list."""
        subreddits = self._get_target_subreddits()
        return "\n".join([f"- r/{sub}" for sub in subreddits])
