"""
Product Hunt Content Generator

Generates complete Product Hunt launch kit:
- Tagline (60 chars)
- Description (260 chars)
- First comment (maker story)
- Topics
- Media checklist
- Hunter outreach template
- Comment response templates

Platform Best Practices (2024):
- Launch at 12:01 AM PST (not midnight your timezone)
- Best days: Tuesday, Wednesday, Thursday (avoid Monday/Friday)
- Tagline: 60 chars MAX, benefit-focused, no buzzwords
- Description: 260 chars MAX, explain what it does for WHO
- First comment: Tell your story (why you built it, not just what it does)
- NEVER ask for upvotes directly (against ToS, can get banned)
- Respond to EVERY comment within 2 hours
- Prepare GIF demos (static images underperform 50%)
- Hunter matters less now, but top hunters still get visibility
- Gallery images: Show the product in action, not just logos
"""

from .base import BasePlatformGenerator
from ..distribution import ProductHuntContent


class ProductHuntGenerator(BasePlatformGenerator):
    """Generate Product Hunt launch kit following 2024 best practices."""

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

    # Best launch days (avoid Monday, Friday, weekends)
    BEST_LAUNCH_DAYS = ["tuesday", "wednesday", "thursday"]

    def generate(self) -> ProductHuntContent:
        """Generate complete Product Hunt kit with comment templates."""
        content = ProductHuntContent(
            tagline=self._generate_tagline(),
            description=self._generate_description(),
            first_comment=self._generate_first_comment(),
            topics=self._get_topics(),
            media_checklist=self._generate_media_checklist(),
            hunter_outreach_template=self._generate_hunter_template(),
            launch_day_prep=self._generate_launch_prep(),
        )

        # Add comment templates as part of launch_day_prep notes
        # (ProductHuntContent doesn't have a comment_templates field,
        # so we append guidance to the first comment)
        comment_guidance = self._generate_comment_guidance()
        content.first_comment += f"\n\n---\n\n{comment_guidance}"

        return content

    def _generate_comment_guidance(self) -> str:
        """Generate guidance for responding to comments."""
        return """**COMMENT RESPONSE GUIDE**

When responding to Product Hunt comments:

✓ Respond to EVERY comment (yes, every single one)
✓ Respond within 2 hours during launch day
✓ Be genuine, not salesy
✓ Thank people specifically (mention something from their comment)
✓ Answer questions thoroughly
✓ Take criticism gracefully (thank them, acknowledge, explain)

For feature requests: "Great idea! Added to our roadmap. Can you share more about your use case?"

For comparisons: "Good question! The main difference is [X]. We built this for [specific user]."

For criticism: "Fair point. Here's what we're doing about it: [action]."
"""

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
        """Generate launch day preparation checklist with timing."""
        return [
            # Week before
            "T-7 days: Email your list a teaser (don't mention exact date)",
            "T-7 days: DM 20-30 supporters asking them to check PH on launch day",
            "T-5 days: Prep all social media posts (Twitter thread, LinkedIn)",
            "T-5 days: Create GIF demos (3-5 seconds each, show key features)",
            "T-3 days: Coordinate with hunter if using one (share all assets)",
            "T-3 days: Write first comment draft, get feedback from 2-3 people",

            # Day before
            "T-1 day: Upload all assets to PH (don't publish yet)",
            "T-1 day: Test EVERY link (signup, docs, pricing, social)",
            "T-1 day: Clear your schedule for launch day",
            "T-1 day: Set 3 alarms: 11:45pm PST, 12:00am PST, 12:05am PST",

            # Launch sequence (12:01am PST is the golden minute)
            "12:01am PST: Publish on Product Hunt",
            "12:05am PST: Post your maker comment immediately",
            "12:10am PST: Post Twitter launch thread",
            "12:15am PST: Post LinkedIn announcement",
            "12:30am PST: Share in relevant Slack/Discord communities",

            # Throughout the day (CRITICAL)
            "Every 30min: Check for new comments and respond",
            "Every 2hrs: Share progress update on Twitter (not upvote counts!)",
            "Afternoon: Share behind-the-scenes content",

            # IMPORTANT: What NOT to do
            "⚠️ NEVER ask for upvotes directly (against ToS)",
            "⚠️ NEVER share direct upvote links (against ToS)",
            "⚠️ DO share: 'We're live on Product Hunt, would love your feedback'",

            # End of day
            "End of day: Thank everyone who commented/supported",
            "Next day: Follow up with everyone who showed interest",
        ]

    def _generate_comment_templates(self) -> dict:
        """Generate templates for responding to PH comments."""
        ctx = self.context

        return {
            "thank_you_positive": [
                f"Thank you so much! Really appreciate you checking out {ctx.product_name}. Let me know if you have any questions as you explore!",
                f"This means a lot! Would love to hear what you think after trying it out.",
                f"Thanks for the support! If you run into any issues, just reply here—I'm monitoring all day.",
            ],
            "feature_request": [
                f"Great suggestion! I've added this to our roadmap. Would you mind sharing a bit more about your use case? It'll help us prioritize.",
                f"Love this idea. We actually have something similar planned for v2. I'll keep you posted when it's ready!",
                f"Thanks for the feedback! Can you tell me more about how you'd use this? I want to make sure we build it right.",
            ],
            "question_about_product": [
                f"Great question! [ANSWER]. Does that help? Happy to clarify further.",
                f"Thanks for asking! [ANSWER]. Let me know if you'd like me to walk you through it.",
            ],
            "comparison_to_competitor": [
                f"Good question! The main difference is [SPECIFIC DIFFERENTIATOR]. We built {ctx.product_name} specifically for [TARGET USER], while [COMPETITOR] is more focused on [THEIR FOCUS]. Happy to dive deeper if helpful!",
            ],
            "pricing_question": [
                f"Great question! {self._get_pricing_statement()}. We wanted to make it accessible for [TARGET]. Let me know if you have specific questions about what's included!",
            ],
            "criticism": [
                f"Appreciate the honest feedback! You make a fair point about [ISSUE]. We're actually working on improving this. Would love to hear more specifics if you have them.",
                f"Thanks for sharing this. You're right that [ACKNOWLEDGE]. Here's what we're doing about it: [ACTION]. Would love your input on the solution.",
            ],
        }

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
