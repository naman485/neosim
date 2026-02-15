"""
Instagram Content Generator

Generates:
- Carousel posts (educational, story-driven)
- Reel concepts (hooks, scripts)
- Stories templates
- Bio optimization
"""

from typing import List
from .base import BasePlatformGenerator
from ..distribution import InstagramContent


class InstagramGenerator(BasePlatformGenerator):
    """Generate Instagram content."""

    # Instagram limits
    MAX_CAPTION_LENGTH = 2200
    OPTIMAL_CAPTION_LENGTH = 150  # For engagement
    MAX_HASHTAGS = 30
    OPTIMAL_HASHTAGS = 5  # Current best practice
    CAROUSEL_MAX_SLIDES = 10

    # Content formats
    CAROUSEL_TYPES = [
        "educational",      # Step-by-step how-to
        "story",           # Journey/transformation
        "listicle",        # Top X tips
        "myth_busting",    # Common misconceptions
        "before_after",    # Transformation
    ]

    REEL_FORMATS = [
        "hook_tutorial",   # Hook + quick tutorial
        "day_in_life",     # Behind the scenes
        "trending_sound",  # Adapt trending audio
        "transformation",  # Before/after
        "talking_head",    # Direct to camera
    ]

    def generate(self) -> List[InstagramContent]:
        """Generate all Instagram content."""
        content = []

        # Launch carousel
        content.append(self._generate_launch_carousel())

        # Educational carousels
        content.extend(self._generate_educational_carousels())

        # Reel concepts
        content.extend(self._generate_reel_concepts())

        # Story templates
        content.extend(self._generate_story_templates())

        # Bio optimization
        content.append(self._generate_bio_content())

        return content

    def _generate_launch_carousel(self) -> InstagramContent:
        """Generate launch announcement carousel."""
        ctx = self.context

        slides = [
            f"Introducing {ctx.product_name}",
            f"The Problem:\n{ctx.pain_points[0] if ctx.pain_points else 'What we solve'}",
            f"The Solution:\n{ctx.unique_value_prop}",
        ]

        # Add feature slides
        for feature in ctx.key_features[:3]:
            slides.append(f"Feature:\n{feature}")

        # Closing slide
        slides.append(f"Try {ctx.product_name} today\nLink in bio")

        caption = f"""Launching {ctx.product_name} today.

{ctx.unique_value_prop}

After months of building, it's finally here.

Swipe through to see what makes it different.

Link in bio to try it free.

{self._format_hashtags()}
"""

        return InstagramContent(
            content_type="carousel",
            caption=self.truncate(caption, self.MAX_CAPTION_LENGTH),
            visual_description="Launch announcement carousel with branded slides",
            carousel_slides=slides,
            hashtags=self.generate_hashtags("instagram", self.OPTIMAL_HASHTAGS),
        )

    def _generate_educational_carousels(self) -> List[InstagramContent]:
        """Generate educational carousel content."""
        ctx = self.context
        carousels = []

        # How-to carousel
        if ctx.key_features:
            slides = [
                f"How to {ctx.product_description.lower()} in 5 steps",
                "Step 1: Identify the problem",
                "Step 2: Define your goals",
                "Step 3: Set up your workflow",
                "Step 4: Execute consistently",
                "Step 5: Measure and optimize",
                f"Or just use {ctx.product_name}\nLink in bio",
            ]

            carousels.append(InstagramContent(
                content_type="carousel",
                caption=f"""The hard way vs. the easy way.

You could spend hours doing this manually...

Or you could use {ctx.product_name} and get it done in minutes.

Which would you choose?

Save this for later.

{self._format_hashtags()}
""",
                visual_description="Educational how-to carousel with numbered steps",
                carousel_slides=slides,
                hashtags=self.generate_hashtags("instagram", self.OPTIMAL_HASHTAGS),
            ))

        # Pain point carousel
        if ctx.pain_points:
            slides = [
                f"Signs you need {ctx.product_name}",
            ]
            for i, pain in enumerate(ctx.pain_points[:5], 1):
                slides.append(f"Sign #{i}:\n{pain}")
            slides.append(f"Sound familiar?\nLink in bio")

            carousels.append(InstagramContent(
                content_type="carousel",
                caption=f"""If you're nodding along, this is for you.

{ctx.product_name} was built for exactly these problems.

Tag someone who needs this.

{self._format_hashtags()}
""",
                visual_description="Pain point awareness carousel",
                carousel_slides=slides,
                hashtags=self.generate_hashtags("instagram", self.OPTIMAL_HASHTAGS),
            ))

        # Myth busting carousel
        carousels.append(InstagramContent(
            content_type="carousel",
            caption=f"""Let's bust some myths about {ctx.category.lower()}.

Swipe to see what's actually true.

Which one surprised you? Comment below.

{self._format_hashtags()}
""",
            visual_description="Myth vs Reality carousel with contrasting slides",
            carousel_slides=[
                f"Myths about {ctx.category}",
                "Myth #1:\n\"It's too complicated\"\n\nReality:\nIt doesn't have to be",
                "Myth #2:\n\"It's too expensive\"\n\nReality:\nROI pays for itself",
                "Myth #3:\n\"I don't have time\"\n\nReality:\nIt saves you time",
                f"The truth?\n{ctx.unique_value_prop}",
            ],
            hashtags=self.generate_hashtags("instagram", self.OPTIMAL_HASHTAGS),
        ))

        return carousels

    def _generate_reel_concepts(self) -> List[InstagramContent]:
        """Generate Reel concepts with hooks and scripts."""
        ctx = self.context
        reels = []

        # Hook + Tutorial Reel
        reels.append(InstagramContent(
            content_type="reel_concept",
            caption=f"""This changed how I {ctx.product_description.lower()}.

Try it yourself: link in bio.

{self._format_hashtags()}
""",
            visual_description="Screen recording showing product in action",
            hashtags=self.generate_hashtags("instagram", self.OPTIMAL_HASHTAGS),
            carousel_slides=[
                "HOOK (0-3s): \"Stop doing [pain point] the hard way\"",
                "PROBLEM (3-8s): Show the frustrating old way",
                f"SOLUTION (8-20s): Demo {ctx.product_name} solving it",
                "CTA (20-25s): \"Link in bio to try free\"",
            ],
        ))

        # Day in the life Reel
        reels.append(InstagramContent(
            content_type="reel_concept",
            caption=f"""A day building {ctx.product_name}.

The highs, the lows, and everything in between.

Follow for more behind the scenes.

{self._format_hashtags()}
""",
            visual_description="Vlog-style founder content",
            hashtags=self.generate_hashtags("instagram", self.OPTIMAL_HASHTAGS),
            carousel_slides=[
                "HOOK (0-3s): \"Building a startup is...(honest take)\"",
                "MORNING (3-10s): Show morning routine/workspace",
                "WORK (10-20s): Coding/designing/customer calls",
                "WIN (20-25s): Small win or user feedback",
                "CTA (25-30s): \"Follow to see if we make it\"",
            ],
        ))

        # Trending format adaptation
        reels.append(InstagramContent(
            content_type="reel_concept",
            caption=f"""POV: You finally found a tool that actually works.

{ctx.product_name} - link in bio.

{self._format_hashtags()}
""",
            visual_description="POV format showing user reaction",
            hashtags=self.generate_hashtags("instagram", self.OPTIMAL_HASHTAGS),
            carousel_slides=[
                "FORMAT: POV reaction trend",
                "SETUP: Show frustration with old way",
                f"REVEAL: Discover {ctx.product_name}",
                "REACTION: Genuine excitement/relief",
                "END: Product demo + CTA",
            ],
        ))

        # Talking head educational
        reels.append(InstagramContent(
            content_type="reel_concept",
            caption=f"""The one thing most {ctx.target_roles[0].lower() if ctx.target_roles else 'people'}s get wrong about {ctx.category.lower()}.

Do you agree?

{self._format_hashtags()}
""",
            visual_description="Founder talking directly to camera",
            hashtags=self.generate_hashtags("instagram", self.OPTIMAL_HASHTAGS),
            carousel_slides=[
                "HOOK (0-3s): \"Here's what nobody tells you about...\"",
                "SETUP (3-10s): Common misconception",
                "INSIGHT (10-20s): The truth + why it matters",
                f"SOLUTION (20-25s): How {ctx.product_name} helps",
                "CTA (25-30s): \"Follow for more tips\"",
            ],
        ))

        return reels

    def _generate_story_templates(self) -> List[InstagramContent]:
        """Generate Story templates."""
        ctx = self.context
        stories = []

        # Launch day story sequence
        stories.append(InstagramContent(
            content_type="story",
            caption="Launch day story sequence",
            visual_description="Multi-slide story sequence for launch day",
            carousel_slides=[
                "STORY 1: Countdown sticker - \"Something big is coming...\"",
                "STORY 2: Behind the scenes prep photo",
                f"STORY 3: \"It's live! {ctx.product_name} is here\" + Link sticker",
                "STORY 4: Screen recording of product",
                "STORY 5: Poll - \"What feature are you most excited about?\"",
                "STORY 6: User reactions/DMs (screenshot)",
                "STORY 7: Thank you + \"Link in bio\"",
            ],
        ))

        # Engagement story
        stories.append(InstagramContent(
            content_type="story",
            caption="Engagement story template",
            visual_description="Interactive story with polls/questions",
            carousel_slides=[
                f"Question sticker: \"What's your biggest challenge with {ctx.category.lower()}?\"",
                "Collect responses and share (with permission)",
                f"\"This is exactly why we built {ctx.product_name}\"",
                "Link sticker to product",
            ],
        ))

        # Feature highlight story
        stories.append(InstagramContent(
            content_type="story",
            caption="Feature highlight story",
            visual_description="Quick feature demo in story format",
            carousel_slides=[
                "STORY 1: \"Did you know?\" hook",
                f"STORY 2: Feature demo (screen recording)",
                "STORY 3: Benefit statement",
                "STORY 4: \"Try it yourself\" + Link sticker",
            ],
        ))

        return stories

    def _generate_bio_content(self) -> InstagramContent:
        """Generate optimized bio content."""
        ctx = self.context

        bio_options = [
            f"{ctx.unique_value_prop}\nBy @yourhandle\nTry free",
            f"Helping {ctx.target_roles[0].lower() if ctx.target_roles else 'you'}s {ctx.product_description.lower()}\nFree to start",
            f"{ctx.product_name}\n{ctx.unique_value_prop}\nLink below",
        ]

        return InstagramContent(
            content_type="bio",
            caption="Bio optimization options",
            visual_description="Instagram bio text options",
            carousel_slides=[
                "BIO OPTION 1:\n" + bio_options[0],
                "BIO OPTION 2:\n" + bio_options[1],
                "BIO OPTION 3:\n" + bio_options[2],
                "BIO TIPS:\n- Use line breaks\n- Include CTA\n- Add relevant emoji (1-2 max)\n- Update link regularly",
            ],
        )

    def _format_hashtags(self) -> str:
        """Format hashtags for Instagram."""
        tags = self.generate_hashtags("instagram", self.OPTIMAL_HASHTAGS)
        return " ".join(tags)
