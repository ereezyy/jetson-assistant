"""
Event bus implementation for inter-component communication.
Uses publish-subscribe pattern to allow loose coupling between components.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import inspect
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Predefined event types for the assistant."""
    # System events
    STARTUP = "system.startup"
    SHUTDOWN = "system.shutdown"
    ERROR = "system.error"
    
    # Audio events
    AUDIO_START = "audio.start"
    AUDIO_STOP = "audio.stop"
    AUDIO_LEVEL = "audio.level"
    
    # Speech recognition events
    SPEECH_START = "speech.start"
    SPEECH_END = "speech.end"
    SPEECH_RESULT = "speech.result"
    
    # TTS events
    TTS_START = "tts.start"
    TTS_END = "tts.end"
    
    # GUI events
    GUI_READY = "gui.ready"
    GUI_UPDATE = "gui.update"
    
    # Skill events
    SKILL_LOADED = "skill.loaded"
    SKILL_ERROR = "skill.error"
    SKILL_RESPONSE = "skill.response"

@dataclass
class Event:
    """Event data class."""
    event_type: EventType
    data: Any = None
    source: str = None
    
    def __str__(self):
        return f"Event({self.event_type}, source={self.source or 'system'})"

class EventBus:
    """Event bus for inter-component communication."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the event bus."""
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._wildcard_subscribers: List[Callable] = []
        self._event_history: List[Tuple[float, Event]] = []
        self._max_history = 1000  # Keep last 1000 events
    
    def subscribe(self, event_type: Optional[EventType] = None):
        """
        Decorator to subscribe a function to an event type.
        
        Args:
            event_type: Event type to subscribe to. If None, subscribes to all events.
            
        Returns:
            Decorator function
        """
        def decorator(func):
            if event_type is None:
                if func not in self._wildcard_subscribers:
                    self._wildcard_subscribers.append(func)
            else:
                if event_type not in self._subscribers:
                    self._subscribers[event_type] = []
                if func not in self._subscribers[event_type]:
                    self._subscribers[event_type].append(func)
            return func
        return decorator
    
    def unsubscribe(self, func: Callable, event_type: Optional[EventType] = None):
        """
        Unsubscribe a function from an event type or all events.
        
        Args:
            func: Function to unsubscribe
            event_type: Event type to unsubscribe from. If None, unsubscribes from all events.
        """
        if event_type is None:
            # Remove from all event types
            for subscribers in self._subscribers.values():
                if func in subscribers:
                    subscribers.remove(func)
            if func in self._wildcard_subscribers:
                self._wildcard_subscribers.remove(func)
        else:
            # Remove from specific event type
            if event_type in self._subscribers and func in self._subscribers[event_type]:
                self._subscribers[event_type].remove(func)
    
    def publish(self, event: Event):
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        if not isinstance(event, Event):
            raise ValueError("Event must be an instance of Event class")
        
        # Add to history
        self._event_history.append((time.time(), event))
        self._event_history = self._event_history[-self._max_history:]
        
        logger.debug(f"Publishing event: {event}")
        
        # Notify specific subscribers
        if event.event_type in self._subscribers:
            for subscriber in self._subscribers[event.event_type]:
                try:
                    self._call_subscriber(subscriber, event)
                except Exception as e:
                    logger.error(f"Error in subscriber for {event.event_type}: {e}", exc_info=True)
        
        # Notify wildcard subscribers
        for subscriber in self._wildcard_subscribers:
            try:
                self._call_subscriber(subscriber, event)
            except Exception as e:
                logger.error(f"Error in wildcard subscriber: {e}", exc_info=True)
    
    def _call_subscriber(self, subscriber: Callable, event: Event):
        """
        Call a subscriber function with the appropriate arguments.
        
        Args:
            subscriber: Subscriber function
            event: Event to pass to the subscriber
        """
        sig = inspect.signature(subscriber)
        params = sig.parameters
        
        if len(params) == 0:
            subscriber()
        elif len(params) == 1:
            subscriber(event)
        else:
            # Try to match parameters by name
            kwargs = {}
            for name, param in params.items():
                if name == 'event':
                    kwargs[name] = event
                elif name == 'event_type':
                    kwargs[name] = event.event_type
                elif name == 'data':
                    kwargs[name] = event.data
                elif name == 'source':
                    kwargs[name] = event.source
                else:
                    if param.default is not inspect.Parameter.empty:
                        kwargs[name] = param.default
            
            # Only call if we can satisfy all required parameters
            required_params = [
                name for name, param in params.items()
                if param.default is inspect.Parameter.empty and param.kind != param.VAR_KEYWORD
            ]
            
            if all(name in kwargs for name in required_params):
                subscriber(**kwargs)
    
    def get_history(self, limit: int = 100) -> List[Tuple[float, Event]]:
        """
        Get recent event history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of (timestamp, event) tuples, most recent first
        """
        return self._event_history[-limit:]

# Global event bus instance
event_bus = EventBus()

def on_event(event_type: Optional[EventType] = None):
    """
    Decorator to subscribe a function to an event type.
    
    Args:
        event_type: Event type to subscribe to. If None, subscribes to all events.
        
    Returns:
        Decorator function
    """
    return event_bus.subscribe(event_type)

def publish(event: Event):
    """
    Publish an event to the global event bus.
    
    Args:
        event: Event to publish
    """
    event_bus.publish(event)
