"""
LinkedIn Content Generator

Generates:
- Personal founder posts (authentic voice)
- Company page posts
- Article outlines
- Connection templates
"""

from typing import List
from .base import BasePlatformGenerator
from ..distribution import LinkedInContent


class LinkedInGenerator(BasePlatformGenerator):
    """Generate LinkedIn content."""

    # LinkedIn limits
    MAX_POST_LENGTH = 3000
    OPTIMAL_POST_LENGTH = 1500  # For engagement
    MAX_ARTICLE_LENGTH = 120000

    # Optimal posting times
    OPTIMAL_TIMES = ["8am", "12pm", "5pm"]  # Local time

    def generate(self) -> List[LinkedInContent]:
        """Generate all LinkedIn content."""
        content = []

        # Launch announcement
        content.append(self._generate_launch_post())

        # Journey/story posts
        content.extend(self._generate_journey_posts())

        # Thought leadership posts
        content.extend(self._generate_thought_leadership())

        # Connection templates
        content.extend(self._generate_connection_content())

        return content

    def _generate_launch_post(self) -> LinkedInContent:
        """Generate launch announcement post."""
        ctx = self.context

        hook = f"After months of building in secret, I'm thrilled to announce: {ctx.product_name} is live."

        body = f"""{hook}

{ctx.unique_value_prop}

Here's what led to this moment:

{self._format_journey_bullets()}

What {ctx.product_name} does:

{self._format_feature_bullets()}

Why I built this:

Every {ctx.target_roles[0].lower() if ctx.target_roles else 'professional'} I talked to struggled with {ctx.pain_points[0].lower() if ctx.pain_points else 'this problem'}. The existing solutions were either too complex, too expensive, or simply didn't work.

{ctx.product_name} is different because {ctx.unique_value_prop.lower()}.

The road ahead:

This is just v1. We have big plans and would love your input on what to build next.

Try it free: [LINK]

---

To everyone who supported this journey - thank you.

To those starting their own building journey - keep going. The world needs what you're creating.

{self._format_hashtags()}
"""

        return LinkedInContent(
            content_type="personal_post",
            text=self.truncate(body, self.MAX_POST_LENGTH),
            hook=hook,
            hashtags=self.generate_hashtags("linkedin", 5),
            optimal_time="8am local",
            call_to_action="Try it free at [LINK]",
        )

    def _generate_journey_posts(self) -> List[LinkedInContent]:
        """Generate founder journey/story posts."""
        ctx = self.context
        posts = []

        # The struggle post
        struggle_hook = f"The hardest part of building {ctx.product_name} wasn't the code."
        posts.append(LinkedInContent(
            content_type="personal_post",
            text=f"""{struggle_hook}

It was staying motivated when nobody cared.

Week 1: Excited, full of energy
Week 4: "Is this even a good idea?"
Week 8: First user feedback (brutal but helpful)
Week 12: Finally starting to see traction

What I learned:

1. The dip is real. Push through it.
2. Early feedback hurts but makes you better.
3. Small wins compound.

If you're building something and feeling stuck - keep going.

The people who succeed aren't smarter. They just don't quit.

{self._format_hashtags()}
""",
            hook=struggle_hook,
            hashtags=self.generate_hashtags("linkedin", 4),
            optimal_time="12pm local",
        ))

        # Lessons learned post
        lessons_hook = f"Building {ctx.product_name} taught me more than my MBA ever could."
        posts.append(LinkedInContent(
            content_type="personal_post",
            text=f"""{lessons_hook}

Here are 7 lessons that shaped our journey:

1. Talk to users before writing code
   (I wasted 3 months building the wrong thing)

2. Simple beats feature-rich
   (Our MVP had 3 features. Users loved it.)

3. Launch before you're ready
   (Perfectionism is procrastination in disguise)

4. Critics are free consultants
   (Every negative review taught us something)

5. Build in public
   (Transparency creates trust)

6. Focus on one thing
   (We said no to 10 features for every 1 we built)

7. Rest is productive
   (Burnout kills more startups than competition)

What's the biggest lesson you've learned while building?

{self._format_hashtags()}
""",
            hook=lessons_hook,
            hashtags=self.generate_hashtags("linkedin", 4),
            optimal_time="8am local",
        ))

        # The pivot post
        pivot_hook = "Our original idea failed. Here's what we did next."
        posts.append(LinkedInContent(
            content_type="personal_post",
            text=f"""{pivot_hook}

Version 1 of {ctx.product_name} was completely different.

Nobody wanted it.

So we did something radical:

We called 50 potential users and asked one question:
"What's your biggest frustration with {ctx.category.lower()}?"

The answer surprised us:
"{ctx.pain_points[0] if ctx.pain_points else 'The existing tools are too complex'}"

We rebuilt from scratch around that insight.

6 weeks later: first paying customer.

The lesson?

The market doesn't care about your vision.
It cares about its problems.

Listen. Adapt. Build.

{self._format_hashtags()}
""",
            hook=pivot_hook,
            hashtags=self.generate_hashtags("linkedin", 4),
            optimal_time="5pm local",
        ))

        return posts

    def _generate_thought_leadership(self) -> List[LinkedInContent]:
        """Generate thought leadership posts."""
        ctx = self.context
        posts = []

        # Industry insight post
        insight_hook = f"The {ctx.category.lower()} industry is broken. Here's why."
        posts.append(LinkedInContent(
            content_type="personal_post",
            text=f"""{insight_hook}

Most tools are built for:
- Enterprise budgets
- Complex use cases
- Feature checklists

But most users need:
- Affordable pricing
- Simple workflows
- Solutions that just work

The gap is massive.

That's why we built {ctx.product_name}.

Not for everyone. For {ctx.target_roles[0].lower() if ctx.target_roles else 'people'}s who want to get things done without the complexity.

The future of {ctx.category.lower()} is:
- Simple
- Affordable
- User-first

Do you agree?

{self._format_hashtags()}
""",
            hook=insight_hook,
            hashtags=self.generate_hashtags("linkedin", 4),
            optimal_time="12pm local",
        ))

        # Prediction post
        prediction_hook = f"My prediction for {ctx.category.lower()} in 2025:"
        posts.append(LinkedInContent(
            content_type="personal_post",
            text=f"""{prediction_hook}

1. AI will handle the boring stuff
   (Focus shifts to strategy, not execution)

2. Simple tools win over feature-packed ones
   (Users are tired of complexity)

3. Pricing becomes more transparent
   (No more "contact sales for pricing")

4. Integration becomes expected
   (Standalone tools die)

5. Community-led growth beats paid ads
   (Trust > impressions)

What did I miss?

{self._format_hashtags()}
""",
            hook=prediction_hook,
            hashtags=self.generate_hashtags("linkedin", 4),
            optimal_time="8am local",
        ))

        return posts

    def _generate_connection_content(self) -> List[LinkedInContent]:
        """Generate connection request and outreach templates."""
        ctx = self.context
        templates = []

        # Connection request template
        templates.append(LinkedInContent(
            content_type="connection_template",
            text=f"""Hi [NAME],

I noticed you're working on {ctx.category.lower()} challenges at [COMPANY].

I'm building {ctx.product_name} - {ctx.product_description}.

Would love to connect and learn more about how you're approaching [specific challenge].

No pitch, just genuinely curious about your perspective.

[YOUR NAME]
""",
            hook="Connection request template",
            optimal_time="N/A",
        ))

        # Post-connection message
        templates.append(LinkedInContent(
            content_type="connection_template",
            text=f"""Thanks for connecting, [NAME]!

Quick question: What's your biggest challenge with {ctx.pain_points[0].lower() if ctx.pain_points else ctx.category.lower()} right now?

Always trying to learn from people in the trenches.

[YOUR NAME]
""",
            hook="Post-connection template",
            optimal_time="N/A",
        ))

        # Product mention (after rapport)
        templates.append(LinkedInContent(
            content_type="connection_template",
            text=f"""Hey [NAME],

Enjoyed our conversation about [TOPIC].

Actually built something that might help with what you mentioned: {ctx.product_name}.

{ctx.unique_value_prop}

Would love your take on it if you have 5 minutes: [LINK]

Either way, great connecting!

[YOUR NAME]
""",
            hook="Soft product intro template",
            optimal_time="N/A",
        ))

        return templates

    def _format_journey_bullets(self) -> str:
        """Format journey bullet points."""
        return """- Started with a frustration I couldn't ignore
- Validated the idea with 50+ conversations
- Built the MVP in [X] weeks
- Launched to our first 10 users
- Iterated based on real feedback"""

    def _format_feature_bullets(self) -> str:
        """Format feature bullets for LinkedIn."""
        features = self.context.key_features[:4] if self.context.key_features else ["Simple setup"]
        bullets = []
        for f in features:
            bullets.append(f"- {f}")
        return "\n".join(bullets)

    def _format_hashtags(self) -> str:
        """Format hashtags for LinkedIn."""
        tags = self.generate_hashtags("linkedin", 5)
        return " ".join(tags)
