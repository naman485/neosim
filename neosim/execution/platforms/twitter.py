"""
Twitter/X Content Generator

Generates:
- Launch thread (7-10 tweets)
- 30 days of daily content
- Engagement hooks
"""

from typing import List
from .base import BasePlatformGenerator
from ..distribution import TwitterContent


class TwitterGenerator(BasePlatformGenerator):
    """Generate Twitter/X content."""

    # Twitter limits
    MAX_TWEET_LENGTH = 280
    THREAD_LENGTH = 8  # Optimal thread length
    DAILY_CONTENT_DAYS = 30

    # Optimal posting times (EST)
    OPTIMAL_TIMES = ["9am", "12pm", "5pm"]

    def generate(self) -> List[TwitterContent]:
        """Generate all Twitter content."""
        content = []

        # Launch thread
        content.extend(self._generate_launch_thread())

        # Daily content
        content.extend(self._generate_daily_content())

        # Engagement hooks
        content.extend(self._generate_engagement_hooks())

        return content

    def _generate_launch_thread(self) -> List[TwitterContent]:
        """Generate 7-10 tweet launch thread."""
        ctx = self.context
        thread = []

        # Tweet 1: Hook
        thread.append(TwitterContent(
            content_type="launch_thread",
            text=self.truncate(
                f"After months of building in the shadows, I'm thrilled to announce {ctx.product_name}.\n\n"
                f"{ctx.unique_value_prop}\n\n"
                f"Here's the story (thread)",
                self.MAX_TWEET_LENGTH
            ),
            thread_position=1,
            hashtags=[],
        ))

        # Tweet 2: The problem
        pain = ctx.pain_points[0] if ctx.pain_points else "a common challenge"
        thread.append(TwitterContent(
            content_type="launch_thread",
            text=self.truncate(
                f"The problem:\n\n"
                f"Every {ctx.target_roles[0] if ctx.target_roles else 'professional'} "
                f"deals with {pain.lower()}.\n\n"
                f"We've all felt that frustration.",
                self.MAX_TWEET_LENGTH
            ),
            thread_position=2,
        ))

        # Tweet 3: Why existing solutions fail
        thread.append(TwitterContent(
            content_type="launch_thread",
            text=self.truncate(
                f"Current solutions?\n\n"
                f"- Too complex\n"
                f"- Too expensive\n"
                f"- Built for enterprises, not real users\n\n"
                f"We needed something different.",
                self.MAX_TWEET_LENGTH
            ),
            thread_position=3,
        ))

        # Tweet 4: The solution
        thread.append(TwitterContent(
            content_type="launch_thread",
            text=self.truncate(
                f"Enter {ctx.product_name}:\n\n"
                f"{ctx.product_description}\n\n"
                f"{self.get_cta()} at [LINK]",
                self.MAX_TWEET_LENGTH
            ),
            thread_position=4,
        ))

        # Tweet 5-6: Key features
        features = ctx.key_features[:4] if ctx.key_features else ["Easy setup", "Fast results"]
        feature_text = "\n".join([f"- {f}" for f in features[:2]])
        thread.append(TwitterContent(
            content_type="launch_thread",
            text=self.truncate(
                f"What makes it different:\n\n{feature_text}",
                self.MAX_TWEET_LENGTH
            ),
            thread_position=5,
        ))

        if len(features) > 2:
            feature_text = "\n".join([f"- {f}" for f in features[2:4]])
            thread.append(TwitterContent(
                content_type="launch_thread",
                text=self.truncate(
                    f"Plus:\n\n{feature_text}",
                    self.MAX_TWEET_LENGTH
                ),
                thread_position=6,
            ))

        # Tweet 7: Pricing/accessibility
        pricing_msg = self._get_pricing_tweet()
        thread.append(TwitterContent(
            content_type="launch_thread",
            text=pricing_msg,
            thread_position=len(thread) + 1,
        ))

        # Tweet 8: CTA
        thread.append(TwitterContent(
            content_type="launch_thread",
            text=self.truncate(
                f"Ready to try {ctx.product_name}?\n\n"
                f"[LINK]\n\n"
                f"Would love your feedback - reply or DM me!\n\n"
                f"RT to help others discover this",
                self.MAX_TWEET_LENGTH
            ),
            thread_position=len(thread) + 1,
            hashtags=self.generate_hashtags("twitter", 3),
        ))

        return thread

    def _generate_daily_content(self) -> List[TwitterContent]:
        """Generate 30 days of daily tweets."""
        ctx = self.context
        content = []

        # Content themes to rotate through
        themes = [
            ("tip", self._tip_templates()),
            ("problem", self._problem_templates()),
            ("feature", self._feature_templates()),
            ("social_proof", self._social_proof_templates()),
            ("behind_scenes", self._behind_scenes_templates()),
        ]

        for day in range(1, self.DAILY_CONTENT_DAYS + 1):
            theme_idx = day % len(themes)
            theme_name, templates = themes[theme_idx]
            template_idx = (day // len(themes)) % len(templates)

            tweet_text = templates[template_idx].format(
                product=ctx.product_name,
                pain_point=ctx.pain_points[0] if ctx.pain_points else "the struggle",
                feature=ctx.key_features[day % len(ctx.key_features)] if ctx.key_features else "our features",
                role=ctx.target_roles[0] if ctx.target_roles else "professionals",
            )

            content.append(TwitterContent(
                content_type="daily",
                text=self.truncate(tweet_text, self.MAX_TWEET_LENGTH),
                optimal_time=self.OPTIMAL_TIMES[day % len(self.OPTIMAL_TIMES)] + " EST",
            ))

        return content

    def _generate_engagement_hooks(self) -> List[TwitterContent]:
        """Generate engagement hooks (questions, polls, CTAs)."""
        ctx = self.context
        hooks = [
            f"What's your biggest challenge with {ctx.category.lower()}?\n\nDrop a comment - curious to hear!",
            f"Hot take: {ctx.unique_value_prop.lower()} shouldn't be hard.\n\nAgree or disagree?",
            f"Building {ctx.product_name} taught me:\n\n1. Listen to users\n2. Ship fast\n3. Iterate constantly\n\nWhat's your building philosophy?",
            f"If you could automate one thing in your workflow, what would it be?",
            f"Unpopular opinion: Most {ctx.category.lower()} tools are overcomplicated.\n\nSimple > Feature-packed\n\nThoughts?",
        ]

        return [
            TwitterContent(
                content_type="engagement_hook",
                text=self.truncate(hook, self.MAX_TWEET_LENGTH),
                engagement_hook=hook.split("\n")[-1] if "\n" in hook else None,
            )
            for hook in hooks
        ]

    def _get_pricing_tweet(self) -> str:
        """Get pricing-related tweet."""
        ctx = self.context
        model = ctx.pricing_model

        if model == "freemium":
            return self.truncate(
                f"The best part? {ctx.product_name} has a generous free tier.\n\n"
                f"No credit card required.\n"
                f"No time limits.\n"
                f"Just sign up and start.",
                self.MAX_TWEET_LENGTH
            )
        elif model == "free-trial":
            days = "14"  # Default
            return self.truncate(
                f"Try {ctx.product_name} free for {days} days.\n\n"
                f"No credit card upfront.\n"
                f"Cancel anytime.\n\n"
                f"See why teams are switching.",
                self.MAX_TWEET_LENGTH
            )
        else:
            return self.truncate(
                f"Pricing starts at just ${ctx.pricing_tiers[0]['price'] if ctx.pricing_tiers else 29}/mo.\n\n"
                f"Affordable for solo builders.\n"
                f"Scalable for teams.",
                self.MAX_TWEET_LENGTH
            )

    def _tip_templates(self) -> List[str]:
        """Tip tweet templates."""
        return [
            "Quick tip: {feature} can save you hours every week.\n\nHere's how",
            "{role}s: Stop doing {pain_point} manually.\n\nUse {product} instead",
            "The secret to {feature}?\n\nConsistency + the right tools",
            "How to get more done:\n\n1. Identify bottlenecks\n2. Automate them\n3. Focus on what matters",
        ]

    def _problem_templates(self) -> List[str]:
        """Problem-focused templates."""
        return [
            "Tired of {pain_point}?\n\nYou're not alone. We built {product} to fix this.",
            "Every {role} has dealt with {pain_point}.\n\nIt doesn't have to be this way.",
            "The old way: {pain_point}\n\nThe new way: {product}",
            "Raise your hand if {pain_point} has ruined your day.\n\n(Mine is up)",
        ]

    def _feature_templates(self) -> List[str]:
        """Feature highlight templates."""
        return [
            "New: {feature} in {product}\n\nYour most requested feature is here",
            "Did you know {product} can {feature}?\n\nMost users miss this",
            "Feature spotlight: {feature}\n\nMakes everything faster",
            "{feature} + {product} = productivity unlocked",
        ]

    def _social_proof_templates(self) -> List[str]:
        """Social proof templates."""
        return [
            "Love seeing {role}s succeed with {product}.\n\nYour wins are our wins",
            "Another team just shipped faster with {product}.\n\nWho's next?",
            "The {product} community is growing!\n\nThanks for believing in us",
            "Feedback from a {role}:\n\n\"[INSERT TESTIMONIAL]\"\n\nThis is why we build.",
        ]

    def _behind_scenes_templates(self) -> List[str]:
        """Behind-the-scenes templates."""
        return [
            "Building {product} in public:\n\nHere's what we shipped this week",
            "The hardest part of building {product}?\n\nSaying no to features",
            "Honest update on {product}:\n\n[SHARE PROGRESS]",
            "Lessons from building {product}:\n\nUsers > features",
        ]
