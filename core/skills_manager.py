"""
Skills Manager for the Jetson TX1 Personal Assistant.
Handles loading, managing, and dispatching to skills.
"""

import importlib
import inspect
import logging
import os
import pkgutil
from typing import Dict, List, Type, Any, Optional, Tuple

from .skills.base_skill import Skill, Intent
from utils.event_bus import Event, EventType, event_bus
from utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class SkillsManager:
    """Manages all skills for the assistant."""
    
    def __init__(self, config: ConfigManager):
        """
        Initialize the skills manager.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.skills: Dict[str, Skill] = {}
        self.skills_dir = os.path.join(os.path.dirname(__file__), 'skills')
        self._load_skills()
    
    def _load_skills(self) -> None:
        """Load all available skills."""
        logger.info("Loading skills...")
        
        # Built-in skills
        builtin_skills = [
            'time_date'
        ]
        
        # Load built-in skills
        for skill_name in builtin_skills:
            self._load_skill(f"core.skills.{skill_name}")
        
        # Load custom skills from the skills directory if it exists
        if os.path.exists(self.skills_dir):
            self._load_skills_from_dir()
        
        logger.info(f"Loaded {len(self.skills)} skills")
    
    def _load_skills_from_dir(self) -> None:
        """Load skills from the skills directory."""
        try:
            # Add the skills directory to the Python path
            import sys
            skills_parent = os.path.dirname(self.skills_dir)
            if skills_parent not in sys.path:
                sys.path.insert(0, skills_parent)
            
            # Import all modules in the skills directory
            for _, name, _ in pkgutil.iter_modules([self.skills_dir]):
                try:
                    self._load_skill(f"skills.{name}")
                except Exception as e:
                    logger.error(f"Failed to load skill {name}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error loading skills from directory: {e}", exc_info=True)
    
    def _load_skill(self, module_path: str) -> bool:
        """
        Load a single skill from a module.
        
        Args:
            module_path: Dotted path to the module (e.g., 'core.skills.time_date')
            
        Returns:
            bool: True if the skill was loaded successfully, False otherwise
        """
        try:
            # Import the module
            module = importlib.import_module(module_path)
            
            # Find all classes that inherit from Skill
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, Skill) and obj != Skill and 
                    obj.__module__ == module.__name__):
                    
                    # Check if the skill is enabled in the config
                    skill_config = self.config.get(f"skills.{obj.__name__.lower()}", {})
                    if not skill_config.get('enabled', True):
                        logger.info(f"Skill {obj.__name__} is disabled in config")
                        continue
                    
                    # Initialize the skill
                    try:
                        skill_instance = obj(skill_config)
                        skill_name = skill_instance.name
                        
                        if skill_name in self.skills:
                            logger.warning(f"Skill with name '{skill_name}' already exists. Overwriting.")
                        
                        self.skills[skill_name] = skill_instance
                        logger.info(f"Loaded skill: {skill_name} (v{skill_instance.version})")
                        
                        # Publish skill loaded event
                        event_bus.publish(Event(
                            event_type=EventType.SKILL_LOADED,
                            data={
                                'name': skill_name,
                                'version': skill_instance.version,
                                'description': skill_instance.description
                            }
                        ))
                        
                        return True
                    except Exception as e:
                        logger.error(f"Failed to initialize skill {name}: {e}", exc_info=True)
                        
                        # Publish skill error event
                        event_bus.publish(Event(
                            event_type=EventType.SKILL_ERROR,
                            data={
                                'module': module_path,
                                'error': str(e)
                            }
                        ))
                        
                        return False
            
            logger.warning(f"No Skill class found in module: {module_path}")
            return False
            
        except ImportError as e:
            logger.error(f"Failed to import skill module {module_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error loading skill {module_path}: {e}", exc_info=True)
            return False
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """
        Get a skill by name.
        
        Args:
            skill_name: Name of the skill to get
            
        Returns:
            The skill instance or None if not found
        """
        return self.skills.get(skill_name)
    
    def get_all_skills(self) -> List[Skill]:
        """
        Get all loaded skills.
        
        Returns:
            List of all loaded skill instances
        """
        return list(self.skills.values())
    
    async def process_text(self, text: str) -> Tuple[Optional[str], Optional[Skill]]:
        """
        Process text input and find a matching skill to handle it.
        
        Args:
            text: Input text to process
            
        Returns:
            Tuple of (response_text, skill) or (None, None) if no match found
        """
        if not text.strip():
            return None, None
        
        best_match = None
        best_intent = None
        highest_confidence = 0.0
        
        # Find the best matching skill and intent
        for skill in self.skills.values():
            try:
                intent = skill.match(text)
                if intent and intent.confidence > highest_confidence:
                    best_match = skill
                    best_intent = intent
                    highest_confidence = intent.confidence
            except Exception as e:
                logger.error(f"Error in skill {skill.name}: {e}", exc_info=True)
        
        # If we found a match, handle it
        if best_match and best_intent:
            logger.info(f"Matched intent: {best_intent} (confidence: {highest_confidence:.2f})")
            try:
                response = await best_match.handle(best_intent)
                return response, best_match
            except Exception as e:
                logger.error(f"Error handling intent with {best_match.name}: {e}", exc_info=True)
                return f"I encountered an error processing that request: {str(e)}", best_match
        
        return None, None
    
    def stop(self) -> None:
        """Stop all skills and clean up resources."""
        logger.info("Stopping all skills...")
        for skill in self.skills.values():
            try:
                skill.stop()
            except Exception as e:
                logger.error(f"Error stopping skill {skill.name}: {e}", exc_info=True)
        
        self.skills.clear()
        logger.info("All skills stopped")
