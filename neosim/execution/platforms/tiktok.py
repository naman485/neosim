"""
TikTok Content Generator

Generates:
- Video hooks (critical first 3 seconds)
- Full video scripts
- Trend adaptations
- Format templates
"""

from typing import List
from .base import BasePlatformGenerator
from ..distribution import TikTokContent


class TikTokGenerator(BasePlatformGenerator):
    """Generate TikTok content."""

    # TikTok specifics
    MAX_CAPTION_LENGTH = 2200
    OPTIMAL_VIDEO_LENGTH = 30  # seconds
    MAX_VIDEO_LENGTH = 180  # 3 minutes

    # Proven TikTok formats
    VIDEO_FORMATS = [
        "hook_tutorial",      # Hook + quick how-to
        "storytime",          # Personal narrative
        "day_in_life",        # Behind the scenes
        "pov",               # POV format
        "before_after",       # Transformation
        "duet_stitch",        # React to content
        "green_screen",       # Explain over screenshot
        "trending_sound",     # Use viral audio
    ]

    # Hook templates that work
    HOOK_TEMPLATES = [
        "Stop scrolling if you...",
        "Nobody talks about this but...",
        "I wish someone told me this earlier...",
        "POV: You just discovered...",
        "The secret to [X] that took me [Y] to learn...",
        "You're doing [X] wrong. Here's why...",
        "This changed everything for me...",
        "Why does nobody talk about...",
        "Unpopular opinion:...",
        "If you're struggling with [X], watch this...",
    ]

    def generate(self) -> List[TikTokContent]:
        """Generate all TikTok content."""
        content = []

        # Launch video
        content.append(self._generate_launch_video())

        # Hook variations
        content.extend(self._generate_hook_variations())

        # Tutorial videos
        content.extend(self._generate_tutorials())

        # Trend adaptations
        content.extend(self._generate_trend_adaptations())

        # Talking head content
        content.extend(self._generate_talking_head())

        return content

    def _generate_launch_video(self) -> TikTokContent:
        """Generate launch announcement video."""
        ctx = self.context

        hook = f"I just launched something that's going to change how you {ctx.product_description.lower()}"

        script = f"""[HOOK - 0-3s]
{hook}

[CONTEXT - 3-8s]
For the past [X] months, I've been building something in secret.

[PROBLEM - 8-12s]
You know how {ctx.pain_points[0].lower() if ctx.pain_points else 'things are frustrating'}?
That's exactly why I built this.

[REVEAL - 12-18s]
Introducing {ctx.product_name}.
[Show product on screen]

[DEMO - 18-25s]
{ctx.unique_value_prop}
[Quick screen recording demo]

[CTA - 25-30s]
Link in bio to try it free.
Follow for updates on the journey.
"""

        return TikTokContent(
            content_type="launch",
            hook_3sec=hook,
            script=script,
            format_template="talking_head_to_demo",
            trending_sounds=["Original audio - building in public"],
        )

    def _generate_hook_variations(self) -> List[TikTokContent]:
        """Generate different hook variations for testing."""
        ctx = self.context
        hooks = []

        # Problem-focused hooks
        pain = ctx.pain_points[0].lower() if ctx.pain_points else "struggling"
        hooks.append(TikTokContent(
            content_type="hook",
            hook_3sec=f"Stop scrolling if you're tired of {pain}",
            script=f"""[HOOK - 0-3s]
Stop scrolling if you're tired of {pain}

[BODY - 3-20s]
I used to spend hours on this.
Then I built something that does it in minutes.
[Demo {ctx.product_name}]

[CTA - 20-30s]
Link in bio. It's free to start.
""",
            format_template="hook_tutorial",
        ))

        # Secret/insider hooks
        hooks.append(TikTokContent(
            content_type="hook",
            hook_3sec=f"The {ctx.category.lower()} tool that nobody's talking about...",
            script=f"""[HOOK - 0-3s]
The {ctx.category.lower()} tool that nobody's talking about...

[REVEAL - 3-8s]
It's called {ctx.product_name}
And it's kind of a game changer

[DEMO - 8-25s]
Here's what it does:
{ctx.unique_value_prop}
[Screen recording]

[CTA - 25-30s]
You're welcome. Link in bio.
""",
            format_template="green_screen",
        ))

        # Unpopular opinion hook
        hooks.append(TikTokContent(
            content_type="hook",
            hook_3sec=f"Unpopular opinion: {ctx.category} doesn't have to be complicated",
            script=f"""[HOOK - 0-3s]
Unpopular opinion: {ctx.category} doesn't have to be complicated

[RANT - 3-15s]
I'm so tired of tools that require a PhD to use.
Most people don't need all those features.
They need something that just works.

[SOLUTION - 15-25s]
That's why I built {ctx.product_name}.
Simple. Effective. Done.
[Quick demo]

[CTA - 25-30s]
Fight me in the comments. Or try it - link in bio.
""",
            format_template="talking_head",
        ))

        # Wish I knew hook
        hooks.append(TikTokContent(
            content_type="hook",
            hook_3sec=f"I wish someone showed me this tool when I started as a {ctx.target_roles[0].lower() if ctx.target_roles else 'founder'}",
            script=f"""[HOOK - 0-3s]
I wish someone showed me this tool when I started

[STORY - 3-12s]
When I was starting out, I wasted so much time on {ctx.pain_points[0].lower() if ctx.pain_points else 'manual work'}.
If only I had something like this...

[REVEAL - 12-22s]
Now I use {ctx.product_name}.
{ctx.unique_value_prop}
[Demo]

[CTA - 22-30s]
Don't make the same mistake I did.
Link in bio - it's free to try.
""",
            format_template="storytime_to_demo",
        ))

        return hooks

    def _generate_tutorials(self) -> List[TikTokContent]:
        """Generate tutorial-style content."""
        ctx = self.context
        tutorials = []

        # Quick tutorial
        tutorials.append(TikTokContent(
            content_type="tutorial",
            hook_3sec=f"How to {ctx.product_description.lower()} in under 60 seconds",
            script=f"""[HOOK - 0-3s]
How to {ctx.product_description.lower()} in under 60 seconds

[STEP 1 - 3-12s]
First, go to [website] and sign up.
It takes 10 seconds.

[STEP 2 - 12-20s]
Next, [key action in product].
This is where the magic happens.

[STEP 3 - 20-28s]
Finally, [result action].
And that's it. Done.

[CTA - 28-30s]
Link in bio. No excuses now.
""",
            format_template="step_by_step",
        ))

        # Feature spotlight
        if ctx.key_features:
            for feature in ctx.key_features[:2]:
                tutorials.append(TikTokContent(
                    content_type="tutorial",
                    hook_3sec=f"This feature in {ctx.product_name} is a game changer",
                    script=f"""[HOOK - 0-3s]
This feature is a game changer

[FEATURE - 3-8s]
{feature}
Let me show you how it works.

[DEMO - 8-25s]
[Screen recording of feature]
[Explain what's happening]

[CTA - 25-30s]
Try it yourself - link in bio.
""",
                    format_template="feature_demo",
                ))

        return tutorials

    def _generate_trend_adaptations(self) -> List[TikTokContent]:
        """Generate trend/format adaptations."""
        ctx = self.context
        trends = []

        # POV format
        trends.append(TikTokContent(
            content_type="trend_adaptation",
            hook_3sec=f"POV: You finally found a {ctx.category.lower()} tool that doesn't suck",
            script=f"""[SETUP - 0-5s]
[Show frustrated face]
[Text overlay: "Me after trying another {ctx.category.lower()} tool"]

[TRANSITION - 5-10s]
[Discovery moment]
[Text: "Then I found {ctx.product_name}"]

[PAYOFF - 10-20s]
[Show relief/excitement]
[Quick demo of product working perfectly]

[CTA - 20-25s]
[Text overlay: "Link in bio"]
[Happy reaction]
""",
            format_template="pov",
            trending_sounds=["Use trending sound - search 'relief' or 'finally'"],
        ))

        # Day in the life
        trends.append(TikTokContent(
            content_type="trend_adaptation",
            hook_3sec="A day in my life building a startup",
            script=f"""[MORNING - 0-8s]
5:30am - Wake up
Coffee and check metrics
[Show dashboard/laptop]

[WORK - 8-18s]
Building features
Customer calls
[Montage of work]

[HIGHLIGHT - 18-25s]
Best part? Seeing users succeed with {ctx.product_name}
[Show user feedback/testimonial]

[CLOSE - 25-30s]
Back at it tomorrow.
Follow for the journey.
""",
            format_template="day_in_life",
            trending_sounds=["Chill lo-fi background"],
        ))

        # Duet/Stitch reaction
        trends.append(TikTokContent(
            content_type="trend_adaptation",
            hook_3sec="[Stitch with relevant creator] Actually, there's a better way...",
            script=f"""[STITCH CLIP - 0-5s]
[Creator talking about common problem]

[YOUR TAKE - 5-25s]
Actually, there's a much easier way to do this.
I built {ctx.product_name} specifically for this.
[Demo the solution]
{ctx.unique_value_prop}

[CTA - 25-30s]
Link in bio if you want to try it.
""",
            format_template="stitch",
            trending_sounds=["Original audio"],
        ))

        return trends

    def _generate_talking_head(self) -> List[TikTokContent]:
        """Generate talking head content."""
        ctx = self.context
        videos = []

        # Founder story
        videos.append(TikTokContent(
            content_type="storytime",
            hook_3sec=f"Why I quit my job to build {ctx.product_name}",
            script=f"""[HOOK - 0-3s]
Why I quit my job to build {ctx.product_name}

[STORY - 3-20s]
I was working at [company], doing [job].
Every day I saw {ctx.pain_points[0].lower() if ctx.pain_points else 'the same problems'}.
Nobody was solving it properly.

So I decided to build the solution myself.

[LESSON - 20-28s]
{ctx.product_name} is that solution.
{ctx.unique_value_prop}

[CTA - 28-30s]
Link in bio. Would love your feedback.
""",
            format_template="talking_head",
        ))

        # Hot take
        videos.append(TikTokContent(
            content_type="hot_take",
            hook_3sec=f"Hot take: Most {ctx.category.lower()} tools are built wrong",
            script=f"""[HOOK - 0-3s]
Hot take: Most {ctx.category.lower()} tools are built wrong

[ARGUMENT - 3-18s]
They're built for power users with huge budgets.
But most people? They need something simple.
Something that just works.
Without the learning curve.
Without the enterprise pricing.

[PITCH - 18-25s]
That's why {ctx.product_name} exists.
{ctx.unique_value_prop}

[CTA - 25-30s]
Am I wrong? Fight me in the comments.
Or try it yourself - link in bio.
""",
            format_template="talking_head",
        ))

        # Tips format
        videos.append(TikTokContent(
            content_type="tips",
            hook_3sec=f"3 things I wish I knew before starting {ctx.category.lower()}",
            script=f"""[HOOK - 0-3s]
3 things I wish I knew earlier

[TIP 1 - 3-10s]
Number 1: Start simple.
You don't need all the features.
You need the right features.

[TIP 2 - 10-18s]
Number 2: Automate early.
Manual work doesn't scale.
Trust me.

[TIP 3 - 18-25s]
Number 3: Use the right tools.
Like {ctx.product_name} (shameless plug).
{ctx.unique_value_prop}

[CTA - 25-30s]
Follow for more tips. Link in bio.
""",
            format_template="talking_head",
        ))

        return videos
