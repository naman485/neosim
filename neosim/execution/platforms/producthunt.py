"""
Product Hunt Content Generator

Generates complete Product Hunt launch kit:
- Tagline (60 chars)
- Description (260 chars)
- First comment (maker story)
- Topics
- Media checklist
- Hunter outreach template
"""

from .base import BasePlatformGenerator
from ..distribution import ProductHuntContent


class ProductHuntGenerator(BasePlatformGenerator):
    """Generate Product Hunt launch kit."""

    # Product Hunt limits
    MAX_TAGLINE_LENGTH = 60
    MAX_DESCRIPTION_LENGTH = 260
    MAX_FIRST_COMMENT_LENGTH = 10000

    # Topic mapping by category
    TOPIC_MAP = {
        "SaaS": ["SaaS", "Productivity", "Tech"],
        "DevTool": ["Developer Tools", "Open Source", "Tech"],
        "Consumer": ["Productivity", "Lifestyle", "Tech"],
        "Marketplace": ["Marketplaces", "Tech"],
        "API": ["Developer Tools", "APIs", "Tech"],
    }

    def generate(self) -> ProductHuntContent:
        """Generate complete Product Hunt kit."""
        return ProductHuntContent(
            tagline=self._generate_tagline(),
            description=self._generate_description(),
            first_comment=self._generate_first_comment(),
            topics=self._get_topics(),
            media_checklist=self._generate_media_checklist(),
            hunter_outreach_template=self._generate_hunter_template(),
            launch_day_prep=self._generate_launch_prep(),
        )

    def _generate_tagline(self) -> str:
        """Generate 60-char tagline."""
        ctx = self.context

        # Options to try, in order of preference
        options = [
            ctx.unique_value_prop,
            f"{ctx.product_description} for {ctx.target_roles[0].lower() if ctx.target_roles else 'teams'}s",
            f"The {ctx.category.lower()} that {ctx.product_description.split()[0].lower()}s for you",
            ctx.product_description,
        ]

        for option in options:
            if len(option) <= self.MAX_TAGLINE_LENGTH:
                return option

        # Truncate the best option
        return self.truncate(ctx.unique_value_prop, self.MAX_TAGLINE_LENGTH)

    def _generate_description(self) -> str:
        """Generate 260-char description."""
        ctx = self.context

        # Build description components
        problem = ctx.pain_points[0].lower() if ctx.pain_points else "complexity"
        solution = ctx.unique_value_prop

        base = f"{ctx.product_name} helps {ctx.target_roles[0].lower() if ctx.target_roles else 'teams'}s {ctx.product_description.lower()}. "

        features = ""
        if ctx.key_features:
            features = f"Features: {', '.join(ctx.key_features[:2])}. "

        cta = self.get_cta() + " today!"

        full = base + features + cta

        if len(full) <= self.MAX_DESCRIPTION_LENGTH:
            return full

        # Try without features
        shorter = base + cta
        if len(shorter) <= self.MAX_DESCRIPTION_LENGTH:
            return shorter

        return self.truncate(base, self.MAX_DESCRIPTION_LENGTH)

    def _generate_first_comment(self) -> str:
        """Generate maker's first comment (story)."""
        ctx = self.context

        return f"""Hey Product Hunt!

I'm [YOUR NAME], the maker of {ctx.product_name}.

**The backstory:**

Like many of you, I've struggled with {ctx.pain_points[0].lower() if ctx.pain_points else 'finding the right tools'}. Every solution I tried was either too complex, too expensive, or simply didn't solve the real problem.

So I decided to build something different.

**What is {ctx.product_name}?**

{ctx.unique_value_prop}

In simple terms: {ctx.product_description}

**Key features:**

{self._format_features()}

**Who is this for?**

{ctx.product_name} is perfect for:
{self._format_audience()}

**What makes us different:**

1. **Simplicity first** - No complex setup, no learning curve
2. **Built by users, for users** - Every feature came from real feedback
3. **Transparent pricing** - {self._get_pricing_statement()}

**Where we're headed:**

This is v1. We have big plans including:
- [UPCOMING FEATURE 1]
- [UPCOMING FEATURE 2]
- [UPCOMING FEATURE 3]

**Special for Product Hunt:**

{self._get_ph_special_offer()}

**Your feedback matters:**

I'd love to hear:
- What do you think?
- What features would make this more useful for you?
- What's missing?

I'll be here all day answering questions. Don't hold back - constructive criticism helps us build something better.

Thank you for checking out {ctx.product_name}!

[YOUR NAME]
Founder, {ctx.product_name}

P.S. Shoutout to [THANK PEOPLE/COMMUNITY]
"""

    def _get_topics(self) -> list:
        """Get relevant Product Hunt topics."""
        category = self.context.category
        return self.TOPIC_MAP.get(category, ["Tech", "Productivity"])

    def _generate_media_checklist(self) -> list:
        """Generate media/assets checklist."""
        ctx = self.context
        return [
            "Logo (240x240, PNG, no text)",
            "Gallery image 1: Hero shot (1270x760)",
            "Gallery image 2: Key feature demo",
            "Gallery image 3: Use case / workflow",
            "Gallery image 4: Social proof / testimonials",
            "Thumbnail GIF (240x240, max 3MB)",
            "Demo video (optional but recommended, 2-3 min)",
            f"OG image for social sharing",
            "Maker photo (personal, not logo)",
            f"Screenshot: {ctx.product_name} dashboard/main UI",
        ]

    def _generate_hunter_template(self) -> str:
        """Generate hunter outreach template."""
        ctx = self.context

        return f"""Hi [HUNTER NAME],

I've been following your hunts and really admire your eye for great products.

I'm launching {ctx.product_name} - {ctx.unique_value_prop.lower()}.

**Quick overview:**
{ctx.product_description}

**Why it might be interesting:**
- Solves a real problem: {ctx.pain_points[0] if ctx.pain_points else 'common pain point'}
- {self._get_traction_placeholder()}
- Built specifically for {ctx.target_roles[0].lower() if ctx.target_roles else 'teams'}s

**What I'm asking:**
Would you consider hunting {ctx.product_name}? I'd be honored to have your support.

I have everything ready:
- All media assets
- First comment (maker story)
- Team ready for launch day engagement

Launch date: [DATE]

Happy to jump on a quick call or share a demo.

Thanks for considering!

[YOUR NAME]
{ctx.product_name}
[YOUR TWITTER/LINKEDIN]
"""

    def _generate_launch_prep(self) -> list:
        """Generate launch day preparation checklist."""
        return [
            "Week before: Notify your email list about upcoming launch",
            "Week before: Prep all social media posts",
            "Week before: Coordinate with hunter (if using one)",
            "Day before: Final check all assets uploaded",
            "Day before: Test all links",
            "Day before: Prepare first comment draft",
            "Launch (12:01am PST): Go live",
            "Launch +5min: Post maker comment",
            "Launch +10min: Share on Twitter with thread",
            "Launch +15min: Post on LinkedIn",
            "Launch +30min: Share in relevant communities",
            "Throughout day: Respond to EVERY comment",
            "Throughout day: Share upvote progress on social",
            "End of day: Thank everyone who supported",
        ]

    def _format_features(self) -> str:
        """Format features for first comment."""
        features = self.context.key_features[:5] if self.context.key_features else ["Easy to use"]
        return "\n".join([f"- **{f}**" for f in features])

    def _format_audience(self) -> str:
        """Format target audience."""
        ctx = self.context
        roles = ctx.target_roles[:3] if ctx.target_roles else ["Professionals"]
        return "\n".join([f"- {role}s dealing with {ctx.pain_points[0].lower() if ctx.pain_points else 'workflow challenges'}" for role in roles])

    def _get_pricing_statement(self) -> str:
        """Get pricing statement."""
        ctx = self.context
        if ctx.pricing_model == "freemium":
            return "Free forever tier available"
        elif ctx.pricing_model == "free-trial":
            return "14-day free trial, no credit card required"
        else:
            if ctx.pricing_tiers:
                return f"Starting at ${ctx.pricing_tiers[0]['price']}/mo"
            return "Affordable pricing for all team sizes"

    def _get_ph_special_offer(self) -> str:
        """Get Product Hunt special offer."""
        ctx = self.context
        if ctx.pricing_model == "freemium":
            return "Product Hunt community gets **3 months of Pro free** with code PRODUCTHUNT"
        else:
            return "Product Hunt community gets **50% off for 3 months** with code PRODUCTHUNT"

    def _get_traction_placeholder(self) -> str:
        """Get traction placeholder."""
        return "[X] users in beta / [X] waitlist signups / [X] MRR"
