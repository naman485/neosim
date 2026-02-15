"""
Reddit Content Generator

Generates:
- Launch posts (authentic, value-first)
- Value posts for sustained engagement
- Comment strategy and rules
"""

from typing import List
from .base import BasePlatformGenerator
from ..distribution import RedditContent


class RedditGenerator(BasePlatformGenerator):
    """Generate Reddit content."""

    # Reddit-specific settings
    MAX_TITLE_LENGTH = 300
    MAX_POST_LENGTH = 40000  # Self-posts

    # Subreddit targeting by category
    SUBREDDIT_MAP = {
        "SaaS": ["SaaS", "startups", "Entrepreneur", "smallbusiness", "indiehackers"],
        "DevTool": ["programming", "webdev", "devops", "coding", "learnprogramming"],
        "Consumer": ["ProductManagement", "startups", "Entrepreneur"],
        "Marketplace": ["startups", "Entrepreneur", "smallbusiness"],
        "API": ["programming", "webdev", "devops", "API_Design"],
    }

    # Content rules by subreddit type
    SUBREDDIT_RULES = {
        "startups": ["No direct links", "Add value first", "Follow Show & Tell format"],
        "SaaS": ["Tag with [Tool]", "Include pricing transparency", "Respond to all comments"],
        "indiehackers": ["Share journey", "Include revenue if possible", "Be authentic"],
        "programming": ["Technical focus only", "No self-promotion in title", "Code examples welcome"],
    }

    def generate(self) -> List[RedditContent]:
        """Generate all Reddit content."""
        content = []

        # Primary launch post
        content.append(self._generate_launch_post())

        # Value posts for different subreddits
        content.extend(self._generate_value_posts())

        # Comment strategy
        content.append(self._generate_comment_strategy())

        return content

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
