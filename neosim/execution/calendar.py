"""
Content Calendar Generator

Generates a 30-day cross-platform posting schedule
optimized for launch momentum and sustained engagement.
"""

from typing import List, Optional
from datetime import date, timedelta
from dataclasses import dataclass

from .distribution import DistributionKit, CalendarEntry


@dataclass
class PlatformTiming:
    """Optimal timing for a platform."""
    platform: str
    best_days: List[str]  # "monday", "tuesday", etc.
    best_times: List[str]  # "9am EST", "12pm EST", etc.
    posts_per_week: int
    launch_day_posts: int


class ContentCalendarGenerator:
    """
    Generate 30-day cross-platform content calendar.

    Orchestrates content across platforms with:
    - Launch day coordination
    - Optimal posting times
    - Content variety
    - Platform-specific cadences
    """

    # Platform timing configurations
    PLATFORM_TIMING = {
        "twitter": PlatformTiming(
            platform="twitter",
            best_days=["tuesday", "wednesday", "thursday"],
            best_times=["9am EST", "12pm EST", "5pm EST"],
            posts_per_week=7,  # Daily
            launch_day_posts=3,
        ),
        "reddit": PlatformTiming(
            platform="reddit",
            best_days=["monday", "tuesday", "saturday"],
            best_times=["10am EST", "2pm EST"],
            posts_per_week=2,
            launch_day_posts=1,
        ),
        "linkedin": PlatformTiming(
            platform="linkedin",
            best_days=["tuesday", "wednesday", "thursday"],
            best_times=["8am local", "12pm local"],
            posts_per_week=3,
            launch_day_posts=1,
        ),
        "producthunt": PlatformTiming(
            platform="producthunt",
            best_days=["tuesday", "wednesday", "thursday"],  # Best launch days
            best_times=["12:01am PST"],
            posts_per_week=0,  # One-time launch
            launch_day_posts=1,
        ),
    }

    # Content type rotation by platform
    CONTENT_ROTATION = {
        "twitter": [
            "tip", "feature", "engagement", "behind_scenes",
            "social_proof", "problem", "feature", "engagement",
        ],
        "reddit": [
            "value_post", "ama", "insight", "value_post",
        ],
        "linkedin": [
            "journey", "thought_leadership", "feature", "journey",
            "social_proof", "thought_leadership",
        ],
    }

    def __init__(
        self,
        kit: DistributionKit,
        config,
        start_date: Optional[date] = None,
        duration_days: int = 30,
    ):
        """
        Initialize calendar generator.

        Args:
            kit: Distribution kit with generated content
            config: NeoSimConfig
            start_date: Calendar start (launch day). Defaults to today.
            duration_days: Calendar duration. Default 30 days.
        """
        self.kit = kit
        self.config = config
        self.start_date = start_date or date.today()
        self.duration_days = duration_days

    def generate(self) -> List[CalendarEntry]:
        """Generate complete content calendar."""
        calendar = []

        # Day 1: Launch day (critical)
        calendar.extend(self._generate_launch_day())

        # Days 2-7: Launch week (high intensity)
        calendar.extend(self._generate_launch_week())

        # Days 8-14: Momentum building (moderate intensity)
        calendar.extend(self._generate_week_two())

        # Days 15-30: Sustained engagement (regular cadence)
        calendar.extend(self._generate_sustain_phase())

        # Sort by day and time
        calendar.sort(key=lambda e: (e.day, self._time_sort_key(e.optimal_time)))

        return calendar

    def _generate_launch_day(self) -> List[CalendarEntry]:
        """Generate launch day (Day 1) entries."""
        entries = []
        launch_date = self.start_date

        # Product Hunt (if included)
        if self.kit.product_hunt:
            entries.append(CalendarEntry(
                day=1,
                date=launch_date,
                platform="producthunt",
                content_type="launch",
                content_preview=self.kit.product_hunt.tagline[:100],
                optimal_time="12:01am PST",
                priority="critical",
                notes="Go live! Post maker comment immediately after.",
            ))

        # Twitter launch thread
        if self.kit.twitter:
            thread = [t for t in self.kit.twitter if t.content_type == "launch_thread"]
            if thread:
                entries.append(CalendarEntry(
                    day=1,
                    date=launch_date,
                    platform="twitter",
                    content_type="launch_thread",
                    content_preview=thread[0].text[:100] if thread else "",
                    optimal_time="6:00am EST",
                    priority="critical",
                    notes="Post full thread. Pin to profile.",
                ))

        # LinkedIn announcement
        if self.kit.linkedin:
            launch_posts = [p for p in self.kit.linkedin if p.content_type == "personal_post"]
            if launch_posts:
                entries.append(CalendarEntry(
                    day=1,
                    date=launch_date,
                    platform="linkedin",
                    content_type="launch_announcement",
                    content_preview=launch_posts[0].hook[:100],
                    optimal_time="8:00am local",
                    priority="critical",
                    notes="Personal post from founder account.",
                ))

        # Reddit (be careful with timing)
        if self.kit.reddit:
            entries.append(CalendarEntry(
                day=1,
                date=launch_date,
                platform="reddit",
                content_type="launch_post",
                content_preview="See Show & Tell format",
                optimal_time="10:00am EST",
                priority="high",
                notes="Post to r/startups first. Follow subreddit rules!",
            ))

        return entries

    def _generate_launch_week(self) -> List[CalendarEntry]:
        """Generate days 2-7 entries."""
        entries = []

        for day in range(2, 8):
            current_date = self.start_date + timedelta(days=day - 1)

            # Twitter: Daily posts
            entries.append(self._create_twitter_entry(day, current_date, priority="high"))

            # LinkedIn: 3 posts in week 1
            if day in [3, 5, 7]:
                entries.append(self._create_linkedin_entry(day, current_date, priority="high"))

            # Reddit: 1 follow-up post mid-week
            if day == 4:
                entries.append(CalendarEntry(
                    day=day,
                    date=current_date,
                    platform="reddit",
                    content_type="value_post",
                    content_preview="Lessons learned from launch week",
                    optimal_time="10:00am EST",
                    priority="normal",
                    notes="Share authentic lessons, not promotion.",
                ))

        return entries

    def _generate_week_two(self) -> List[CalendarEntry]:
        """Generate days 8-14 entries."""
        entries = []

        for day in range(8, 15):
            current_date = self.start_date + timedelta(days=day - 1)

            # Twitter: Daily
            entries.append(self._create_twitter_entry(day, current_date))

            # LinkedIn: 2-3 posts in week 2
            if day in [9, 11, 14]:
                entries.append(self._create_linkedin_entry(day, current_date))

            # Reddit: 1 value post
            if day == 10:
                entries.append(CalendarEntry(
                    day=day,
                    date=current_date,
                    platform="reddit",
                    content_type="value_post",
                    content_preview="Technical deep-dive or lessons",
                    optimal_time="2:00pm EST",
                    priority="normal",
                ))

        return entries

    def _generate_sustain_phase(self) -> List[CalendarEntry]:
        """Generate days 15-30 entries."""
        entries = []

        for day in range(15, self.duration_days + 1):
            current_date = self.start_date + timedelta(days=day - 1)
            weekday = current_date.strftime("%A").lower()

            # Twitter: 5 posts per week (weekdays)
            if weekday in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
                entries.append(self._create_twitter_entry(day, current_date))

            # LinkedIn: 2 posts per week
            if weekday in ["tuesday", "thursday"]:
                entries.append(self._create_linkedin_entry(day, current_date))

            # Reddit: 1 post per week (Saturday)
            if weekday == "saturday" and day % 7 == 0:
                entries.append(CalendarEntry(
                    day=day,
                    date=current_date,
                    platform="reddit",
                    content_type="value_post",
                    content_preview="Weekly insight or update",
                    optimal_time="10:00am EST",
                    priority="normal",
                ))

        return entries

    def _create_twitter_entry(
        self,
        day: int,
        entry_date: date,
        priority: str = "normal",
    ) -> CalendarEntry:
        """Create a Twitter calendar entry."""
        # Rotate content types
        rotation = self.CONTENT_ROTATION["twitter"]
        content_type = rotation[(day - 1) % len(rotation)]

        # Get preview from kit
        preview = self._get_twitter_preview(day, content_type)

        # Rotate times
        times = ["9:00am EST", "12:00pm EST", "5:00pm EST"]
        optimal_time = times[(day - 1) % len(times)]

        return CalendarEntry(
            day=day,
            date=entry_date,
            platform="twitter",
            content_type=content_type,
            content_preview=preview,
            optimal_time=optimal_time,
            priority=priority,
        )

    def _create_linkedin_entry(
        self,
        day: int,
        entry_date: date,
        priority: str = "normal",
    ) -> CalendarEntry:
        """Create a LinkedIn calendar entry."""
        rotation = self.CONTENT_ROTATION["linkedin"]
        content_type = rotation[(day - 1) % len(rotation)]

        preview = self._get_linkedin_preview(day, content_type)

        return CalendarEntry(
            day=day,
            date=entry_date,
            platform="linkedin",
            content_type=content_type,
            content_preview=preview,
            optimal_time="8:00am local",
            priority=priority,
        )

    def _get_twitter_preview(self, day: int, content_type: str) -> str:
        """Get preview text for Twitter entry."""
        daily = [t for t in self.kit.twitter if t.content_type == "daily"]
        if daily and day - 1 < len(daily):
            return daily[day - 1].text[:100]
        return f"[{content_type.title()} content for day {day}]"

    def _get_linkedin_preview(self, day: int, content_type: str) -> str:
        """Get preview text for LinkedIn entry."""
        posts = self.kit.linkedin
        if posts:
            # Rotate through available posts
            idx = (day - 1) % len(posts)
            return posts[idx].hook[:100]
        return f"[{content_type.title()} content for day {day}]"

    def _time_sort_key(self, time_str: str) -> int:
        """Convert time string to sortable int (minutes from midnight)."""
        if not time_str:
            return 0

        time_str = time_str.lower()

        # Extract hour
        hour = 0
        if "am" in time_str or "pm" in time_str:
            parts = time_str.replace("am", " am").replace("pm", " pm").split()
            if parts:
                try:
                    time_part = parts[0].replace(":", "")
                    if ":" in parts[0]:
                        h, m = parts[0].split(":")
                        hour = int(h)
                    else:
                        hour = int(time_part)

                    if "pm" in time_str and hour != 12:
                        hour += 12
                    elif "am" in time_str and hour == 12:
                        hour = 0
                except ValueError:
                    pass

        return hour * 60

    def export_csv(self, path: str) -> None:
        """Export calendar to CSV."""
        import csv

        calendar = self.generate()

        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'day', 'date', 'platform', 'content_type',
                'preview', 'time', 'priority', 'notes'
            ])
            writer.writeheader()

            for entry in calendar:
                writer.writerow({
                    'day': entry.day,
                    'date': entry.date.isoformat() if entry.date else '',
                    'platform': entry.platform,
                    'content_type': entry.content_type,
                    'preview': entry.content_preview,
                    'time': entry.optimal_time,
                    'priority': entry.priority,
                    'notes': entry.notes,
                })
