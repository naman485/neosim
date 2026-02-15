"""
Distribution Bridge - Platform Content Generation

Converts simulation results into ready-to-post content for major
distribution platforms: Twitter, Reddit, LinkedIn, Product Hunt.

Usage:
    from neosim.execution.distribution import DistributionGenerator

    generator = DistributionGenerator(simulation_result, config)
    kit = generator.generate()
    generator.export("distribution_kit.json")
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import json


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class TwitterContent:
    """Twitter/X content item."""
    content_type: str  # "launch_thread", "daily", "engagement_hook"
    text: str
    thread_position: Optional[int] = None  # For threads: 1, 2, 3...
    hashtags: List[str] = field(default_factory=list)
    optimal_time: str = "10am EST"
    engagement_hook: Optional[str] = None  # Question or CTA at end


@dataclass
class RedditContent:
    """Reddit content item."""
    content_type: str  # "launch_post", "value_post", "comment"
    title: str
    body: str
    target_subreddits: List[str] = field(default_factory=list)
    flair: Optional[str] = None
    engagement_rules: List[str] = field(default_factory=list)


@dataclass
class LinkedInContent:
    """LinkedIn content item."""
    content_type: str  # "personal_post", "company_post", "article"
    text: str
    hook: str  # First line hook
    hashtags: List[str] = field(default_factory=list)
    optimal_time: str = "8am local"
    call_to_action: Optional[str] = None


@dataclass
class ProductHuntContent:
    """Product Hunt launch kit."""
    tagline: str  # 60 char max
    description: str  # 260 char max
    first_comment: str  # Maker's story
    topics: List[str] = field(default_factory=list)
    media_checklist: List[str] = field(default_factory=list)
    hunter_outreach_template: str = ""
    launch_day_prep: List[str] = field(default_factory=list)


@dataclass
class InstagramContent:
    """Instagram content item (future)."""
    content_type: str  # "carousel", "reel_concept", "story"
    caption: str
    visual_description: str
    hashtags: List[str] = field(default_factory=list)
    carousel_slides: List[str] = field(default_factory=list)


@dataclass
class TikTokContent:
    """TikTok content item (future)."""
    content_type: str  # "hook", "script", "trend_adaptation"
    hook_3sec: str  # Critical first 3 seconds
    script: str
    format_template: str
    trending_sounds: List[str] = field(default_factory=list)


@dataclass
class CalendarEntry:
    """Single calendar entry."""
    day: int  # Day 1, 2, 3... from launch
    date: Optional[date] = None
    platform: str = ""
    content_type: str = ""
    content_preview: str = ""  # First 100 chars
    optimal_time: str = ""
    priority: str = "normal"  # "critical", "high", "normal"
    notes: str = ""


@dataclass
class DistributionKit:
    """Complete distribution content kit."""
    # Metadata
    simulation_id: str = ""
    product_name: str = ""
    generated_at: str = ""

    # Platform content
    twitter: List[TwitterContent] = field(default_factory=list)
    reddit: List[RedditContent] = field(default_factory=list)
    linkedin: List[LinkedInContent] = field(default_factory=list)
    product_hunt: Optional[ProductHuntContent] = None
    instagram: List[InstagramContent] = field(default_factory=list)
    tiktok: List[TikTokContent] = field(default_factory=list)

    # Cross-platform
    content_calendar: List[CalendarEntry] = field(default_factory=list)
    launch_day_playbook: Dict[str, List[str]] = field(default_factory=dict)
    engagement_templates: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "metadata": {
                "simulation_id": self.simulation_id,
                "product_name": self.product_name,
                "generated_at": self.generated_at,
            },
            "platforms": {
                "twitter": {
                    "launch_thread": [
                        {"position": t.thread_position, "text": t.text, "hashtags": t.hashtags}
                        for t in self.twitter if t.content_type == "launch_thread"
                    ],
                    "daily_content": [
                        {"text": t.text, "time": t.optimal_time, "type": t.content_type}
                        for t in self.twitter if t.content_type == "daily"
                    ],
                    "engagement_hooks": [
                        t.text for t in self.twitter if t.content_type == "engagement_hook"
                    ],
                },
                "reddit": {
                    "posts": [
                        {
                            "type": r.content_type,
                            "title": r.title,
                            "body": r.body,
                            "subreddits": r.target_subreddits,
                            "rules": r.engagement_rules,
                        }
                        for r in self.reddit
                    ],
                },
                "linkedin": {
                    "posts": [
                        {
                            "type": li.content_type,
                            "hook": li.hook,
                            "text": li.text,
                            "hashtags": li.hashtags,
                            "time": li.optimal_time,
                        }
                        for li in self.linkedin
                    ],
                },
                "product_hunt": {
                    "tagline": self.product_hunt.tagline if self.product_hunt else "",
                    "description": self.product_hunt.description if self.product_hunt else "",
                    "first_comment": self.product_hunt.first_comment if self.product_hunt else "",
                    "topics": self.product_hunt.topics if self.product_hunt else [],
                    "media_checklist": self.product_hunt.media_checklist if self.product_hunt else [],
                    "hunter_outreach": self.product_hunt.hunter_outreach_template if self.product_hunt else "",
                } if self.product_hunt else None,
                "instagram": {
                    "content": [
                        {
                            "type": ig.content_type,
                            "caption": ig.caption,
                            "visual_description": ig.visual_description,
                            "slides": ig.carousel_slides,
                            "hashtags": ig.hashtags,
                        }
                        for ig in self.instagram
                    ],
                } if self.instagram else None,
                "tiktok": {
                    "content": [
                        {
                            "type": tt.content_type,
                            "hook_3sec": tt.hook_3sec,
                            "script": tt.script,
                            "format": tt.format_template,
                            "sounds": tt.trending_sounds,
                        }
                        for tt in self.tiktok
                    ],
                } if self.tiktok else None,
            },
            "content_calendar": [
                {
                    "day": entry.day,
                    "date": entry.date.isoformat() if entry.date else None,
                    "platform": entry.platform,
                    "content_type": entry.content_type,
                    "preview": entry.content_preview,
                    "time": entry.optimal_time,
                    "priority": entry.priority,
                }
                for entry in self.content_calendar
            ],
            "launch_playbook": self.launch_day_playbook,
            "engagement_templates": self.engagement_templates,
        }


# =============================================================================
# Distribution Generator
# =============================================================================

class DistributionGenerator:
    """
    Orchestrates content generation across all platforms.

    Takes simulation results and config, delegates to platform-specific
    generators, and assembles the complete distribution kit.
    """

    SUPPORTED_PLATFORMS = ["twitter", "reddit", "linkedin", "producthunt", "instagram", "tiktok"]

    def __init__(
        self,
        simulation_result,
        config,
        platforms: Optional[List[str]] = None,
        calendar_start: Optional[date] = None,
    ):
        """
        Initialize distribution generator.

        Args:
            simulation_result: Result from neosim simulation
            config: NeoSimConfig with product/ICP details
            platforms: List of platforms to generate for (default: all supported)
            calendar_start: Start date for content calendar (default: today)
        """
        self.result = simulation_result
        self.config = config
        self.platforms = platforms or self.SUPPORTED_PLATFORMS
        self.calendar_start = calendar_start or date.today()

        # Lazy-load platform generators
        self._generators = {}

    def _get_generator(self, platform: str):
        """Get or create platform generator."""
        if platform not in self._generators:
            if platform == "twitter":
                from .platforms.twitter import TwitterGenerator
                self._generators[platform] = TwitterGenerator(self.result, self.config)
            elif platform == "reddit":
                from .platforms.reddit import RedditGenerator
                self._generators[platform] = RedditGenerator(self.result, self.config)
            elif platform == "linkedin":
                from .platforms.linkedin import LinkedInGenerator
                self._generators[platform] = LinkedInGenerator(self.result, self.config)
            elif platform == "producthunt":
                from .platforms.producthunt import ProductHuntGenerator
                self._generators[platform] = ProductHuntGenerator(self.result, self.config)
            elif platform == "instagram":
                from .platforms.instagram import InstagramGenerator
                self._generators[platform] = InstagramGenerator(self.result, self.config)
            elif platform == "tiktok":
                from .platforms.tiktok import TikTokGenerator
                self._generators[platform] = TikTokGenerator(self.result, self.config)
        return self._generators.get(platform)

    def generate(self) -> DistributionKit:
        """Generate complete distribution kit."""
        kit = DistributionKit(
            simulation_id=getattr(self.result, 'sim_id', 'unknown'),
            product_name=self.config.product.name,
            generated_at=datetime.now().isoformat(),
        )

        # Generate platform content
        if "twitter" in self.platforms:
            gen = self._get_generator("twitter")
            if gen:
                kit.twitter = gen.generate()

        if "reddit" in self.platforms:
            gen = self._get_generator("reddit")
            if gen:
                kit.reddit = gen.generate()

        if "linkedin" in self.platforms:
            gen = self._get_generator("linkedin")
            if gen:
                kit.linkedin = gen.generate()

        if "producthunt" in self.platforms:
            gen = self._get_generator("producthunt")
            if gen:
                kit.product_hunt = gen.generate()

        if "instagram" in self.platforms:
            gen = self._get_generator("instagram")
            if gen:
                kit.instagram = gen.generate()

        if "tiktok" in self.platforms:
            gen = self._get_generator("tiktok")
            if gen:
                kit.tiktok = gen.generate()

        # Generate cross-platform content
        kit.content_calendar = self._generate_calendar(kit)
        kit.launch_day_playbook = self._generate_playbook()
        kit.engagement_templates = self._generate_engagement_templates()

        return kit

    def _generate_calendar(self, kit: DistributionKit) -> List[CalendarEntry]:
        """Generate 30-day content calendar."""
        from .calendar import ContentCalendarGenerator

        calendar_gen = ContentCalendarGenerator(
            kit=kit,
            config=self.config,
            start_date=self.calendar_start,
        )
        return calendar_gen.generate()

    def _generate_playbook(self) -> Dict[str, List[str]]:
        """Generate launch day playbook."""
        product = self.config.product

        return {
            "t_minus_24h": [
                "Warm up audience with teaser content",
                "Notify beta users about upcoming launch",
                "Prepare all assets and links",
                "Test all landing page CTAs",
                "Queue social posts for optimal times",
            ],
            "t_minus_1h": [
                "Final check: PH listing ready",
                "Notify hunter (if using one)",
                "Have team ready to engage",
                "Open all social platforms",
            ],
            "launch_hour": [
                f"Post {product.name} on Product Hunt (12:01am PST)",
                "Post Twitter launch thread immediately after",
                "Post LinkedIn announcement",
                "Share in relevant communities (respect rules!)",
                "Reply to first PH comment yourself",
            ],
            "first_4h": [
                "Respond to EVERY Product Hunt comment",
                "Engage with all Twitter replies",
                "DM supporters thanking them",
                "Share behind-the-scenes content",
            ],
            "first_24h": [
                "Continue responding to all engagement",
                "Post follow-up content on each platform",
                "Email your list with launch news",
                "Reach out to relevant journalists/bloggers",
                "Track metrics and adjust messaging",
            ],
        }

    def _generate_engagement_templates(self) -> Dict[str, List[str]]:
        """Generate engagement/reply templates."""
        product = self.config.product
        objections = []
        if hasattr(self.result, 'final_metrics'):
            objections = self.result.final_metrics.objection_clusters[:3]

        templates = {
            "thank_you": [
                f"Thanks so much for the support! Really means a lot.",
                f"Appreciate you checking out {product.name}!",
                f"Thank you! Let me know if you have any questions.",
            ],
            "question_response": [
                "Great question! {answer}",
                "Absolutely - {answer}",
                "{answer} - let me know if that helps!",
            ],
            "objection_handling": [
                {
                    "objection": obj.theme,
                    "responses": [obj.suggested_counter],
                }
                for obj in objections
            ] if objections else [],
            "ask_for_feedback": [
                f"Would love to hear your thoughts on {product.name}!",
                "What would make this more useful for you?",
                "Any features you'd like to see?",
            ],
        }

        return templates

    def export(self, path: str) -> None:
        """Export distribution kit to JSON file."""
        kit = self.generate()
        with open(path, 'w') as f:
            json.dump(kit.to_dict(), f, indent=2)
