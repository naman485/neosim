"""
LLM Content Enhancer

Uses Claude API to polish and improve generated content.
Activated via the --enhance flag on neosim distribute.

Features:
- Improves clarity and engagement
- Maintains platform-specific constraints
- Personalizes content based on ICP
- Optimizes hooks and CTAs
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .distribution import (
    DistributionKit,
    TwitterContent,
    RedditContent,
    LinkedInContent,
    ProductHuntContent,
)


@dataclass
class EnhancementConfig:
    """Configuration for content enhancement."""
    tone: str = "professional yet approachable"
    style: str = "concise and punchy"
    preserve_structure: bool = True
    max_retries: int = 2


class ContentEnhancer:
    """
    Enhances distribution content using Claude API.

    Takes template-generated content and polishes it for:
    - Better engagement
    - Stronger hooks
    - More natural voice
    - Platform-optimized formatting
    """

    # Platform-specific enhancement prompts
    PLATFORM_PROMPTS = {
        "twitter": """You are an expert Twitter/X copywriter. Enhance this tweet while:
- Keeping it under 280 characters
- Making the hook more compelling
- Adding urgency or curiosity
- Maintaining authenticity (no corporate speak)
- Using line breaks strategically for readability""",

        "reddit": """You are an expert Reddit writer. Enhance this post while:
- Maintaining authentic, non-promotional tone
- Following Reddit conventions (no marketing speak)
- Adding value-first content
- Making it feel like a genuine community member wrote it
- Keeping the vulnerability and honesty""",

        "linkedin": """You are an expert LinkedIn content creator. Enhance this post while:
- Creating a strong opening hook (first line is crucial)
- Using strategic line breaks for mobile readability
- Maintaining professional but personable tone
- Adding thought-provoking elements
- Ending with engagement prompt""",

        "producthunt": """You are an expert Product Hunt launcher. Enhance this content while:
- Making the tagline punchy and memorable (max 60 chars)
- Keeping description compelling (max 260 chars)
- Making first comment feel genuine and story-driven
- Highlighting unique value clearly
- Creating urgency without being pushy""",
    }

    def __init__(
        self,
        config: EnhancementConfig = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize enhancer.

        Args:
            config: Enhancement configuration
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.config = config or EnhancementConfig()
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._client = None

    @property
    def client(self):
        """Lazy-load Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package required for enhancement. "
                    "Install with: pip install anthropic"
                )
        return self._client

    def enhance_kit(
        self,
        kit: DistributionKit,
        platforms: Optional[List[str]] = None,
        on_progress: Optional[callable] = None,
    ) -> DistributionKit:
        """
        Enhance all content in distribution kit.

        Args:
            kit: Distribution kit to enhance
            platforms: Specific platforms to enhance (default: all)
            on_progress: Callback for progress updates

        Returns:
            Enhanced distribution kit
        """
        platforms = platforms or ["twitter", "reddit", "linkedin", "producthunt"]

        total_items = self._count_items(kit, platforms)
        current = 0

        # Enhance Twitter
        if "twitter" in platforms and kit.twitter:
            for i, tweet in enumerate(kit.twitter):
                kit.twitter[i] = self._enhance_twitter(tweet)
                current += 1
                if on_progress:
                    on_progress(current, total_items, f"Twitter ({i+1}/{len(kit.twitter)})")

        # Enhance Reddit
        if "reddit" in platforms and kit.reddit:
            for i, post in enumerate(kit.reddit):
                kit.reddit[i] = self._enhance_reddit(post)
                current += 1
                if on_progress:
                    on_progress(current, total_items, f"Reddit ({i+1}/{len(kit.reddit)})")

        # Enhance LinkedIn
        if "linkedin" in platforms and kit.linkedin:
            for i, post in enumerate(kit.linkedin):
                kit.linkedin[i] = self._enhance_linkedin(post)
                current += 1
                if on_progress:
                    on_progress(current, total_items, f"LinkedIn ({i+1}/{len(kit.linkedin)})")

        # Enhance Product Hunt
        if "producthunt" in platforms and kit.product_hunt:
            kit.product_hunt = self._enhance_producthunt(kit.product_hunt)
            current += 1
            if on_progress:
                on_progress(current, total_items, "Product Hunt")

        return kit

    def _count_items(self, kit: DistributionKit, platforms: List[str]) -> int:
        """Count total items to enhance."""
        count = 0
        if "twitter" in platforms:
            count += len(kit.twitter)
        if "reddit" in platforms:
            count += len(kit.reddit)
        if "linkedin" in platforms:
            count += len(kit.linkedin)
        if "producthunt" in platforms and kit.product_hunt:
            count += 1
        return count

    def _enhance_twitter(self, tweet: TwitterContent) -> TwitterContent:
        """Enhance a single tweet."""
        enhanced_text = self._call_llm(
            platform="twitter",
            content=tweet.text,
            constraints={"max_length": 280},
            context={
                "content_type": tweet.content_type,
                "thread_position": tweet.thread_position,
            },
        )

        # Ensure we stay within limits
        if len(enhanced_text) <= 280:
            tweet.text = enhanced_text

        return tweet

    def _enhance_reddit(self, post: RedditContent) -> RedditContent:
        """Enhance a Reddit post."""
        # Enhance title
        enhanced_title = self._call_llm(
            platform="reddit",
            content=post.title,
            constraints={"max_length": 300, "type": "title"},
            context={"subreddits": post.target_subreddits},
        )

        if len(enhanced_title) <= 300:
            post.title = enhanced_title

        # Enhance body
        enhanced_body = self._call_llm(
            platform="reddit",
            content=post.body,
            constraints={"type": "body"},
            context={
                "subreddits": post.target_subreddits,
                "content_type": post.content_type,
            },
        )

        post.body = enhanced_body

        return post

    def _enhance_linkedin(self, post: LinkedInContent) -> LinkedInContent:
        """Enhance a LinkedIn post."""
        enhanced_text = self._call_llm(
            platform="linkedin",
            content=post.text,
            constraints={"max_length": 3000},
            context={"content_type": post.content_type},
        )

        if len(enhanced_text) <= 3000:
            post.text = enhanced_text
            # Extract new hook (first line)
            lines = enhanced_text.strip().split("\n")
            if lines:
                post.hook = lines[0]

        return post

    def _enhance_producthunt(self, ph: ProductHuntContent) -> ProductHuntContent:
        """Enhance Product Hunt content."""
        # Enhance tagline
        enhanced_tagline = self._call_llm(
            platform="producthunt",
            content=ph.tagline,
            constraints={"max_length": 60, "type": "tagline"},
        )

        if len(enhanced_tagline) <= 60:
            ph.tagline = enhanced_tagline

        # Enhance description
        enhanced_desc = self._call_llm(
            platform="producthunt",
            content=ph.description,
            constraints={"max_length": 260, "type": "description"},
        )

        if len(enhanced_desc) <= 260:
            ph.description = enhanced_desc

        # Enhance first comment
        enhanced_comment = self._call_llm(
            platform="producthunt",
            content=ph.first_comment,
            constraints={"type": "first_comment"},
        )

        ph.first_comment = enhanced_comment

        return ph

    def _call_llm(
        self,
        platform: str,
        content: str,
        constraints: Dict[str, Any],
        context: Dict[str, Any] = None,
    ) -> str:
        """
        Call Claude API to enhance content.

        Args:
            platform: Target platform
            content: Content to enhance
            constraints: Platform constraints (max_length, etc.)
            context: Additional context

        Returns:
            Enhanced content
        """
        system_prompt = self.PLATFORM_PROMPTS.get(platform, "Enhance this content.")

        # Build constraint string
        constraint_str = ""
        if "max_length" in constraints:
            constraint_str += f"\nMAX LENGTH: {constraints['max_length']} characters. This is a hard limit."
        if "type" in constraints:
            constraint_str += f"\nCONTENT TYPE: {constraints['type']}"

        # Build context string
        context_str = ""
        if context:
            context_str = "\nCONTEXT: " + ", ".join(f"{k}={v}" for k, v in context.items())

        user_prompt = f"""Enhance this content. Return ONLY the enhanced content, no explanations.

{constraint_str}
{context_str}

ORIGINAL CONTENT:
{content}

ENHANCED CONTENT:"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
            )

            enhanced = response.content[0].text.strip()

            # Basic validation
            if not enhanced:
                return content

            return enhanced

        except Exception as e:
            # On error, return original content
            print(f"Enhancement error: {e}")
            return content

    def enhance_single(
        self,
        platform: str,
        content: str,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Enhance a single piece of content.

        Useful for testing or one-off enhancements.

        Args:
            platform: Target platform
            content: Content to enhance
            constraints: Optional constraints

        Returns:
            Enhanced content
        """
        constraints = constraints or {}
        return self._call_llm(platform, content, constraints)


def enhance_distribution_kit(
    kit: DistributionKit,
    platforms: Optional[List[str]] = None,
    on_progress: Optional[callable] = None,
) -> DistributionKit:
    """
    Convenience function to enhance a distribution kit.

    Args:
        kit: Distribution kit to enhance
        platforms: Specific platforms (default: all)
        on_progress: Progress callback

    Returns:
        Enhanced distribution kit
    """
    enhancer = ContentEnhancer()
    return enhancer.enhance_kit(kit, platforms, on_progress)
