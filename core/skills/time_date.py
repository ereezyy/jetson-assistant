"""
Time and Date skill for the Jetson TX1 Personal Assistant.
Provides information about the current time, date, and timezone.
"""

import datetime
import pytz
from typing import Dict, Any, Optional
import logging

from .base_skill import Skill, intent, SkillPriority
from utils.event_bus import Event, EventType, event_bus

logger = logging.getLogger(__name__)

class TimeDateSkill(Skill):
    """Skill for handling time and date related queries."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the time and date skill."""
        super().__init__(config)
        self.timezone = self.config.get('timezone')
        if self.timezone and self.timezone not in pytz.all_timezones:
            logger.warning(f"Unknown timezone: {self.timezone}. Using system timezone.")
            self.timezone = None
    
    @property
    def name(self) -> str:
        """Return the skill name."""
        return "time_date"
    
    @property
    def description(self) -> str:
        """Return a brief description of the skill."""
        return "Provides information about the current time, date, and timezone."
    
    @property
    def version(self) -> str:
        """Return the version of the skill."""
        return "1.0.0"
    
    def get_current_time(self, timezone_str: str = None) -> datetime.datetime:
        """
        Get the current time in the specified timezone.
        
        Args:
            timezone_str: Timezone string (e.g., 'America/New_York'). If None, uses the configured timezone.
            
        Returns:
            Datetime object with timezone information
        """
        tz = pytz.timezone(timezone_str) if timezone_str else self._get_timezone()
        return datetime.datetime.now(tz)
    
    def _get_timezone(self):
        """Get the configured timezone or system default."""
        if self.timezone:
            return pytz.timezone(self.timezone)
        return pytz.utc  # Default to UTC if no timezone is configured
    
    def format_time(self, dt: datetime.datetime, include_date: bool = False) -> str:
        """
        Format a datetime object as a human-readable string.
        
        Args:
            dt: Datetime object to format
            include_date: Whether to include the date in the output
            
        Returns:
            Formatted time string
        """
        if include_date:
            return dt.strftime("%A, %B %d, %Y at %I:%M %p")
        return dt.strftime("%I:%M %p")
    
    @intent(["what time is it", "what's the time", "current time"], priority=SkillPriority.HIGH)
    async def handle_time_query(self, entities: Dict[str, Any] = None) -> str:
        """Handle time queries."""
        timezone = entities.get('timezone') if entities else None
        current_time = self.get_current_time(timezone)
        time_str = self.format_time(current_time)
        return f"The current time is {time_str}."
    
    @intent(["what's today's date", "what is today's date", "current date"], priority=SkillPriority.HIGH)
    async def handle_date_query(self, entities: Dict[str, Any] = None) -> str:
        """Handle date queries."""
        timezone = entities.get('timezone') if entities else None
        current_time = self.get_current_time(timezone)
        date_str = current_time.strftime("%A, %B %d, %Y")
        return f"Today is {date_str}."
    
    @intent(["what day is it", "what day is today"], priority=SkillPriority.HIGH)
    async def handle_day_query(self, entities: Dict[str, Any] = None) -> str:
        """Handle day of the week queries."""
        timezone = entities.get('timezone') if entities else None
        current_time = self.get_current_time(timezone)
        day_str = current_time.strftime("%A")
        return f"Today is {day_str}."
    
    @intent(re.compile(r"time in (?P<location>[\w\s]+)", re.IGNORECASE))
    async def handle_time_in_location(self, entities: Dict[str, Any] = None) -> str:
        """Handle time in specific location queries."""
        if not entities or 'location' not in entities:
            return "I'm not sure which location you're asking about."
        
        location = entities['location'].lower()
        timezone_map = {
            'new york': 'America/New_York',
            'london': 'Europe/London',
            'paris': 'Europe/Paris',
            'tokyo': 'Asia/Tokyo',
            'sydney': 'Australia/Sydney',
            'los angeles': 'America/Los_Angeles',
            'chicago': 'America/Chicago',
            'beijing': 'Asia/Shanghai',
            'moscow': 'Europe/Moscow',
            'berlin': 'Europe/Berlin'
        }
        
        timezone_str = timezone_map.get(location)
        if not timezone_str:
            return f"I don't know the timezone for {location}."
        
        try:
            current_time = self.get_current_time(timezone_str)
            time_str = self.format_time(current_time, include_date=True)
            return f"The current time in {location.title()} is {time_str}."
        except Exception as e:
            logger.error(f"Error getting time for {location}: {e}")
            return f"I couldn't get the time for {location}."
    
    @intent(["what time is it in"], requires_location=True)
    async def handle_time_in_location_alt(self, entities: Dict[str, Any] = None) -> str:
        """Alternative handler for time in location queries."""
        return await self.handle_time_in_location(entities)
    
    @intent(["set timezone", "change timezone"])
    async def handle_set_timezone(self, entities: Dict[str, Any] = None) -> str:
        """Handle timezone change requests."""
        if not entities or 'timezone' not in entities:
            return "Please specify a timezone, for example: 'Set timezone to America/New_York'"
        
        timezone_str = entities['timezone']
        if timezone_str not in pytz.all_timezones:
            return f"I don't recognize the timezone '{timezone_str}'. Please use a valid timezone like 'America/New_York'."
        
        self.timezone = timezone_str
        return f"Timezone set to {timezone_str}."
    
    @intent(["what's my timezone", "current timezone"])
    async def handle_timezone_query(self) -> str:
        """Handle timezone queries."""
        tz = self.timezone or "system default"
        return f"Your current timezone is set to {tz}."
    
    @intent(["time until"], requires_entity="target_time")
    async def handle_time_until(self, entities: Dict[str, Any] = None) -> str:
        """Handle time until a specific time or event."""
        if not entities or 'target_time' not in entities:
            return "I'm not sure what time or event you're asking about."
        
        # This is a simplified implementation
        # In a real app, you'd want to parse the target time/date
        return "I'm sorry, I can't calculate that yet. This feature is coming soon!"
    
    @intent(["set alarm", "set a timer"], requires_entity="duration")
    async def handle_set_alarm(self, entities: Dict[str, Any] = None) -> str:
        """Handle alarm and timer requests."""
        if not entities or 'duration' not in entities:
            return "Please specify a duration, for example: 'Set a timer for 5 minutes'"
        
        # This is a simplified implementation
        return "I'm sorry, I can't set alarms or timers yet. This feature is coming soon!"
    
    def stop(self):
        """Clean up resources."""
        logger.info("TimeDate skill is shutting down")
