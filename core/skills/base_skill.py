"""
Base class for all skills in the Jetson TX1 Personal Assistant.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Type, Callable
import re
import logging
from enum import Enum

from utils.event_bus import Event, EventType, event_bus, on_event

logger = logging.getLogger(__name__)

class SkillPriority(Enum):
    """Priority levels for skill matching."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class Intent:
    """Represents a user intent matched by a skill."""
    name: str
    confidence: float = 1.0
    entities: Dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""
    
    def __str__(self):
        return f"Intent(name='{self.name}', confidence={self.confidence:.2f})"

class Skill(ABC):
    """
    Abstract base class for all skills.
    
    To create a new skill, inherit from this class and implement the required methods.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the skill.
        
        Args:
            config: Skill-specific configuration
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.priority = SkillPriority.NORMAL
        self._handlers = []
        self._register_handlers()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the skill."""
        pass
    
    @property
    def description(self) -> str:
        """Return a brief description of the skill."""
        return ""
    
    @property
    def version(self) -> str:
        """Return the version of the skill."""
        return "1.0.0"
    
    def _register_handlers(self):
        """Register all handlers decorated with @intent_handler."""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, '_intent_handlers'):
                for pattern, priority in attr._intent_handlers:
                    self._handlers.append((pattern, attr, priority))
    
    def match(self, text: str) -> Optional[Intent]:
        """
        Check if this skill can handle the given text.
        
        Args:
            text: Input text to match against
            
        Returns:
            Intent if matched, None otherwise
        """
        if not self.enabled:
            return None
            
        best_match = None
        highest_confidence = 0.0
        
        for pattern, handler, priority in self._handlers:
            # Try regex match first
            if hasattr(pattern, 'pattern'):  # It's a compiled regex
                match = pattern.search(text)
                if match:
                    confidence = self._calculate_confidence(text, match, priority)
                    if confidence > highest_confidence:
                        entities = match.groupdict()
                        best_match = Intent(
                            name=f"{self.name}.{handler.__name__}",
                            confidence=confidence,
                            entities=entities,
                            raw_text=text
                        )
                        highest_confidence = confidence
            # Then try string matching
            elif isinstance(pattern, str) and pattern.lower() in text.lower():
                confidence = self._calculate_confidence(text, None, priority)
                if confidence > highest_confidence:
                    best_match = Intent(
                        name=f"{self.name}.{handler.__name__}",
                        confidence=confidence,
                        raw_text=text
                    )
                    highest_confidence = confidence
            # Then try callable matcher
            elif callable(pattern):
                result = pattern(text)
                if result:
                    confidence = result.get('confidence', 0.5)
                    if confidence > highest_confidence:
                        best_match = Intent(
                            name=f"{self.name}.{handler.__name__}",
                            confidence=confidence,
                            entities=result.get('entities', {}),
                            raw_text=text
                        )
                        highest_confidence = confidence
        
        return best_match if best_match and highest_confidence > 0.5 else None
    
    def _calculate_confidence(self, text: str, match, priority: SkillPriority) -> float:
        """
        Calculate the confidence score for a match.
        
        Args:
            text: Original input text
            match: Regex match object or None
            priority: Priority level of the handler
            
        Returns:
            Confidence score between 0 and 1
        """
        # Base confidence based on priority
        confidence = 0.3 + (priority.value * 0.2)
        
        # Boost for regex matches with groups
        if match and hasattr(match, 'groupdict') and match.groupdict():
            confidence += 0.1
        
        # Cap at 1.0
        return min(1.0, confidence)
    
    async def handle(self, intent: Intent) -> str:
        """
        Handle a matched intent.
        
        Args:
            intent: Matched intent
            
        Returns:
            Response text
        """
        if not self.enabled:
            return "This skill is currently disabled."
        
        # Extract the handler name from the intent name (format: skill_name.handler_name)
        handler_name = intent.name.split('.')[-1] if '.' in intent.name else intent.name
        handler = getattr(self, handler_name, None)
        
        if not handler or not callable(handler):
            return f"Sorry, I can't handle that request right now."
        
        try:
            # Call the handler with entities if it accepts them
            sig = inspect.signature(handler)
            params = sig.parameters
            
            if 'entities' in params:
                return await handler(entities=intent.entities)
            elif 'intent' in params:
                return await handler(intent=intent)
            else:
                return await handler()
                
        except Exception as e:
            logger.error(f"Error in skill '{self.name}': {e}", exc_info=True)
            return "I encountered an error processing that request."
    
    def stop(self):
        """Clean up resources when the skill is stopped."""
        pass

# Decorators for skill methods
def intent(pattern, priority: SkillPriority = SkillPriority.NORMAL):
    """
    Decorator to mark a method as an intent handler.
    
    Args:
        pattern: String, regex pattern, or callable to match against input text
        priority: Priority level for matching
    """
    def decorator(func):
        if not hasattr(func, '_intent_handlers'):
            func._intent_handlers = []
        
        # Compile regex if it's a string
        if isinstance(pattern, str):
            try:
                # Convert simple patterns to regex
                if not (pattern.startswith('^') or pattern.endswith('$')):
                    # If it's not already a regex, make it a simple word match
                    regex_pattern = r'\b' + re.escape(pattern.lower()) + r'\b'
                else:
                    regex_pattern = pattern
                
                compiled = re.compile(regex_pattern, re.IGNORECASE)
                func._intent_handlers.append((compiled, priority))
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern}': {e}")
                # Fall back to string matching
                func._intent_handlers.append((pattern, priority))
        else:
            func._intent_handlers.append((pattern, priority))
            
        return func
    return decorator

# Example skill implementation
class ExampleSkill(Skill):
    """Example skill demonstrating the skill interface."""
    
    @property
    def name(self) -> str:
        return "example"
    
    @property
    def description(self) -> str:
        return "An example skill for demonstration purposes"
    
    @intent("say hello", priority=SkillPriority.HIGH)
    async def handle_hello(self):
        """Respond to greetings."""
        return "Hello! How can I help you today?"
    
    @intent(re.compile(r"what('?s| is) your name\\?", re.IGNORECASE))
    async def handle_name_query(self):
        """Respond to name queries."""
        return "I'm the Jetson TX1 Personal Assistant!"
    
    def stop(self):
        """Clean up resources."""
        logger.info("Example skill is shutting down")
