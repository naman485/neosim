"""
Twitter/X Content Generator

Generates:
- Launch thread (7-10 tweets)
- 30 days of daily content
- Engagement hooks

Platform Best Practices (2024):
- 280 character limit per tweet
- Threads: 7-10 tweets optimal, first tweet is CRITICAL
- NO "RT to help" or "like if you agree" (algorithm penalizes)
- Hook patterns: Pattern interrupt, curiosity gap, bold statement, numbers
- Best days: Tuesday, Wednesday, Thursday
- Best times: 8-10am EST, 12-1pm EST (tech audience)
- Hashtags: 1-2 max, at the end only
- Line breaks for readability
- End with clear CTA or question (not begging for engagement)
"""

from typing import List
from .base import BasePlatformGenerator
from ..distribution import TwitterContent


class TwitterGenerator(BasePlatformGenerator):
    """Generate Twitter/X content following 2024 best practices."""

    # Twitter limits
    MAX_TWEET_LENGTH = 280
    THREAD_LENGTH = 8  # Optimal thread length (7-10 range)
    DAILY_CONTENT_DAYS = 30

    # Optimal posting times (EST) - tech audience research
    OPTIMAL_TIMES = ["8:30am EST", "12:00pm EST", "5:30pm EST"]

    # Best days for engagement
    BEST_DAYS = ["tuesday", "wednesday", "thursday"]

    # Hook patterns that work
    HOOK_PATTERNS = [
        "bold_statement",    # "Most [X] fail because..."
        "curiosity_gap",     # "The secret most [X] don't know..."
        "pattern_interrupt", # Start with unexpected statement
        "number_hook",       # "I spent [X] hours/days/$ on..."
        "contrarian",        # "Unpopular opinion: [X]"
    ]

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
        """
        Generate 7-10 tweet launch thread.

        Structure:
        1. Hook (pattern interrupt - NO "I'm excited to announce")
        2. Problem (relatable pain)
        3. Why existing solutions fail
        4. Solution intro
        5-6. Key features/differentiators
        7. Pricing/accessibility
        8. CTA (specific, not begging)
        """
        ctx = self.context
        thread = []
        total_tweets = 8

        # Get first pain point for hook
        pain = ctx.pain_points[0] if ctx.pain_points else "a frustrating problem"
        role = ctx.target_roles[0] if ctx.target_roles else "professional"

        # Tweet 1: HOOK - Pattern interrupt (NOT "After months of building...")
        # Use curiosity gap or bold statement
        hook_options = [
            f"Every {role.lower()} I know has this problem:\n\n{pain}\n\nSo I built something to fix it.\n\n🧵 (1/{total_tweets})",
            f"{pain.capitalize()}?\n\nI spent 6 months solving this.\n\nHere's what I built 🧵 (1/{total_tweets})",
            f"The {ctx.category.lower()} tools everyone uses are broken.\n\nHere's why—and what I built instead.\n\n🧵 (1/{total_tweets})",
        ]

        thread.append(TwitterContent(
            content_type="launch_thread",
            text=self.truncate(hook_options[0], self.MAX_TWEET_LENGTH),
            thread_position=1,
            hashtags=[],
            optimal_time="8:30am EST",
        ))

        # Tweet 2: The problem (make it relatable, specific)
        thread.append(TwitterContent(
            content_type="launch_thread",
            text=self.truncate(
                f"The problem:\n\n"
                f"If you're a {role.lower()}, you've probably spent hours on {pain.lower()}.\n\n"
                f"It's frustrating. It's time-consuming.\n\n"
                f"And the existing tools? They make it worse. (2/{total_tweets})",
                self.MAX_TWEET_LENGTH
            ),
            thread_position=2,
        ))

        # Tweet 3: Why existing solutions fail (be specific, not generic)
        thread.append(TwitterContent(
            content_type="launch_thread",
            text=self.truncate(
                f"I tried every tool out there.\n\n"
                f"The problems:\n\n"
                f"→ Too complex (setup takes days)\n"
                f"→ Too expensive (enterprise pricing for basic features)\n"
                f"→ Too slow (waiting for results)\n\n"
                f"So I decided to build something better. (3/{total_tweets})",
                self.MAX_TWEET_LENGTH
            ),
            thread_position=3,
        ))

        # Tweet 4: The solution (benefit-focused, not feature-focused)
        thread.append(TwitterContent(
            content_type="launch_thread",
            text=self.truncate(
                f"Introducing {ctx.product_name}:\n\n"
                f"{ctx.unique_value_prop}\n\n"
                f"Built specifically for {role.lower()}s who want to {ctx.product_description.lower()}. (4/{total_tweets})",
                self.MAX_TWEET_LENGTH
            ),
            thread_position=4,
        ))

        # Tweet 5: Key differentiators (show don't tell)
        features = ctx.key_features[:4] if ctx.key_features else ["Simple setup", "Fast results"]
        thread.append(TwitterContent(
            content_type="launch_thread",
            text=self.truncate(
                f"What makes {ctx.product_name} different:\n\n"
                f"✓ {features[0]}\n"
                f"✓ {features[1] if len(features) > 1 else 'Works out of the box'}\n\n"
                f"No PhD required. No enterprise budget needed. (5/{total_tweets})",
                self.MAX_TWEET_LENGTH
            ),
            thread_position=5,
        ))

        # Tweet 6: More features or social proof
        if len(features) > 2:
            thread.append(TwitterContent(
                content_type="launch_thread",
                text=self.truncate(
                    f"And there's more:\n\n"
                    f"✓ {features[2]}\n"
                    f"{'✓ ' + features[3] if len(features) > 3 else ''}\n\n"
                    f"Every feature came from real user feedback. (6/{total_tweets})",
                    self.MAX_TWEET_LENGTH
                ),
                thread_position=6,
            ))

        # Tweet 7: Pricing/accessibility (transparency builds trust)
        pricing_msg = self._get_pricing_tweet(total_tweets)
        thread.append(TwitterContent(
            content_type="launch_thread",
            text=pricing_msg,
            thread_position=7,
        ))

        # Tweet 8: CTA (specific action, NOT "RT to help")
        thread.append(TwitterContent(
            content_type="launch_thread",
            text=self.truncate(
                f"Try {ctx.product_name} today:\n\n"
                f"[LINK]\n\n"
                f"Questions? Reply here—I read every response.\n\n"
                f"What's the #1 thing you'd want this to solve? (8/{total_tweets})",
                self.MAX_TWEET_LENGTH
            ),
            thread_position=8,
            hashtags=[],  # No hashtags in final tweet - cleaner
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
                optimal_time=self.OPTIMAL_TIMES[day % len(self.OPTIMAL_TIMES)],  # Already includes timezone
            ))

        return content

    def _generate_engagement_hooks(self) -> List[TwitterContent]:
        """
        Generate engagement hooks that drive real conversation.

        Rules:
        - NO "like if you agree" or "RT to help"
        - Ask specific questions, not generic ones
        - Share genuine opinions/takes
        - Make it easy to reply with something specific
        """
        ctx = self.context
        role = ctx.target_roles[0] if ctx.target_roles else "builder"
        pain = ctx.pain_points[0] if ctx.pain_points else "common challenges"

        hooks = [
            # Specific question (easy to answer)
            f"Quick poll for {role.lower()}s:\n\n"
            f"How much time do you spend on {pain.lower()} each week?\n\n"
            f"A) Less than 1 hour\n"
            f"B) 1-3 hours\n"
            f"C) 3-5 hours\n"
            f"D) Way too much",

            # Contrarian take (sparks debate)
            f"Controversial opinion:\n\n"
            f"Most {ctx.category.lower()} tools are built by people who've never actually used them.\n\n"
            f"That's why they're so frustrating.\n\n"
            f"Am I wrong?",

            # Share learnings (provides value)
            f"3 things I learned building {ctx.product_name}:\n\n"
            f"1. Simple beats feature-rich (every time)\n"
            f"2. Users know best—listen to them\n"
            f"3. Ship fast, fix later\n\n"
            f"What would you add?",

            # Specific scenario question
            f"Question for {role.lower()}s:\n\n"
            f"If you had to pick ONE thing to improve in your current workflow, what would it be?\n\n"
            f"(Genuine question—I'm always looking for ideas)",

            # Behind-the-scenes insight
            f"Here's something I almost didn't ship:\n\n"
            f"[SPECIFIC FEATURE] in {ctx.product_name}.\n\n"
            f"I thought it was too simple. Users told me it was their favorite.\n\n"
            f"Lesson: Trust user feedback over your instincts.",

            # Relatable pain point
            f"The worst part of being a {role.lower()}?\n\n"
            f"Spending more time on {pain.lower()} than actually building.\n\n"
            f"What's your biggest time sink?",
        ]

        return [
            TwitterContent(
                content_type="engagement_hook",
                text=self.truncate(hook, self.MAX_TWEET_LENGTH),
                engagement_hook="specific_question",
                optimal_time="12:00pm EST",  # Lunch time = more engagement
            )
            for hook in hooks
        ]

    def _get_pricing_tweet(self, total_tweets: int = 8) -> str:
        """Get pricing-related tweet with transparency."""
        ctx = self.context
        model = ctx.pricing_model

        if model == "freemium":
            return self.truncate(
                f"Pricing:\n\n"
                f"→ Free tier (no credit card)\n"
                f"→ No artificial limits\n"
                f"→ Upgrade when YOU'RE ready\n\n"
                f"I hate bait-and-switch pricing. So {ctx.product_name} doesn't have it. (7/{total_tweets})",
                self.MAX_TWEET_LENGTH
            )
        elif model == "free-trial":
            return self.truncate(
                f"Pricing:\n\n"
                f"→ 14-day free trial\n"
                f"→ No credit card upfront\n"
                f"→ Cancel in 2 clicks\n\n"
                f"You'll know within a week if this is for you. (7/{total_tweets})",
                self.MAX_TWEET_LENGTH
            )
        elif model == "usage-based":
            return self.truncate(
                f"Pricing:\n\n"
                f"→ Pay only for what you use\n"
                f"→ Free to start\n"
                f"→ Scales with your needs\n\n"
                f"No surprise bills. No hidden fees. (7/{total_tweets})",
                self.MAX_TWEET_LENGTH
            )
        else:
            price = ctx.pricing_tiers[0]['price'] if ctx.pricing_tiers else 29
            return self.truncate(
                f"Pricing:\n\n"
                f"→ Starts at ${price}/mo\n"
                f"→ Built for individuals & small teams\n"
                f"→ Cancel anytime\n\n"
                f"Enterprise pricing? We don't do that here. (7/{total_tweets})",
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
