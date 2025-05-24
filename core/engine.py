"""
Core engine for the Jetson TX1 Personal Assistant.
Orchestrates all components including speech recognition, TTS, and skills.
"""

import asyncio
import logging
import queue
import threading
import time
from typing import Dict, Any, Optional, Callable, Awaitable

from utils.config_manager import ConfigManager
from utils.event_bus import Event, EventType, event_bus
from core.skills_manager import SkillsManager

logger = logging.getLogger(__name__)

class AssistantEngine:
    """Main engine for the personal assistant."""
    
    def __init__(self, config: ConfigManager):
        """
        Initialize the assistant engine.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.running = False
        self.event_loop = None
        self.audio_queue = queue.Queue()
        self.skills_manager = None
        self._init_components()
    
    def _init_components(self) -> None:
        """Initialize all components."""
        logger.info("Initializing components...")
        
        # Initialize skills manager
        self.skills_manager = SkillsManager(self.config)
        
        # Initialize other components (will be implemented as needed)
        self._init_audio()
        self._init_speech()
        self._init_tts()
        
        # Register event handlers
        self._register_event_handlers()
    
    def _init_audio(self) -> None:
        """Initialize audio components."""
        # This will be implemented to handle audio input/output
        logger.debug("Audio components initialized")
    
    def _init_speech(self) -> None:
        """Initialize speech recognition."""
        # This will be implemented to handle speech recognition
        logger.debug("Speech recognition initialized")
    
    def _init_tts(self) -> None:
        """Initialize text-to-speech."""
        # This will be implemented to handle text-to-speech
        logger.debug("TTS initialized")
    
    def _register_event_handlers(self) -> None:
        """Register event handlers."""
        event_bus.subscribe(EventType.SHUTDOWN)(self.stop)
        
        @event_bus.subscribe(EventType.SPEECH_RESULT)
        def handle_speech(event: Event):
            """Handle speech recognition results."""
            if not event.data or 'text' not in event.data:
                return
                
            text = event.data['text']
            logger.info(f"Processing speech: {text}")
            
            # Run the processing in the event loop
            asyncio.run_coroutine_threadsafe(
                self.process_text(text),
                self.event_loop
            )
    
    async def process_text(self, text: str) -> None:
        """
        Process text input and generate a response.
        
        Args:
            text: Input text to process
        """
        if not text.strip():
            return
        
        # Publish speech recognized event
        event_bus.publish(Event(
            event_type=EventType.SPEECH_RECOGNIZED,
            data={'text': text}
        ))
        
        # Process the text with skills
        response, skill = await self.skills_manager.process_text(text)
        
        if response:
            # Publish response event
            event_bus.publish(Event(
                event_type=EventType.RESPONSE_GENERATED,
                data={
                    'text': response,
                    'skill': skill.name if skill else None
                }
            ))
            
            # Speak the response
            event_bus.publish(Event(
                event_type=EventType.TTS_SAY,
                data={'text': response}
            ))
    
    def start(self) -> None:
        """Start the assistant engine."""
        if self.running:
            logger.warning("Assistant is already running")
            return
        
        logger.info("Starting assistant engine...")
        self.running = True
        
        # Create a new event loop for this thread
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        
        try:
            # Publish startup event
            event_bus.publish(Event(
                event_type=EventType.STARTUP,
                data={'version': '1.0.0'}
            ))
            
            # Start the event loop
            self.event_loop.run_forever()
            
        except Exception as e:
            logger.critical(f"Fatal error in assistant engine: {e}", exc_info=True)
            raise
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the assistant engine and clean up resources."""
        if not self.running:
            return
        
        logger.info("Stopping assistant engine...")
        self.running = False
        
        # Stop all skills
        if self.skills_manager:
            self.skills_manager.stop()
        
        # Stop the event loop
        if self.event_loop and self.event_loop.is_running():
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)
        
        # Publish shutdown event
        event_bus.publish(Event(event_type=EventType.SHUTDOWN))
        logger.info("Assistant engine stopped")
