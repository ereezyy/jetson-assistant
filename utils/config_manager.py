"""
Configuration manager for the Jetson TX1 Personal Assistant.
Handles loading, validating, and accessing configuration settings.
"""

import os
import yaml
from typing import Any, Dict, Optional

class ConfigManager:
    """Manages configuration settings for the assistant."""
    
    def __init__(self, config_path: str):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the YAML configuration file.
        """
        self.config_path = config_path
        self._config = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from the YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")
        
        # Validate the configuration
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate the configuration values."""
        # Ensure required sections exist
        required_sections = ['wake_word', 'audio', 'speech', 'tts', 'gui', 'logging']
        for section in required_sections:
            if section not in self._config:
                self._config[section] = {}
        
        # Set default values for required settings
        defaults = {
            'wake_word': {
                'enabled': True,
                'word': 'Jetson',
                'sensitivity': 0.5,
                'engine': 'porcupine'
            },
            'audio': {
                'input_device': None,
                'output_device': None,
                'sample_rate': 16000,
                'channels': 1,
                'chunk_size': 1024,
                'timeout': 5,
                'energy_threshold': 300
            },
            'speech': {
                'engine': 'google',
                'language': 'en-US',
                'offline_mode': False
            },
            'tts': {
                'engine': 'gtts',
                'voice': 'en-US',
                'volume': 1.0,
                'rate': 1.0,
                'pitch': 1.0
            },
            'gui': {
                'enabled': True,
                'theme': 'dark',
                'always_on_top': False,
                'start_minimized': False,
                'show_waveform': True
            },
            'logging': {
                'level': 'INFO',
                'file': 'assistant.log',
                'max_size': 10,
                'backup_count': 3
            }
        }
        
        # Apply defaults for missing values
        for section, section_defaults in defaults.items():
            if section not in self._config:
                self._config[section] = section_defaults
            else:
                for key, value in section_defaults.items():
                    if key not in self._config[section]:
                        self._config[section][key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Dot-notation key (e.g., 'gui.theme')
            default: Default value if key is not found
            
        Returns:
            The configuration value or default if not found
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key: Dot-notation key (e.g., 'gui.theme')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self) -> None:
        """Save the current configuration to the config file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self._config, f, default_flow_style=False, sort_keys=False)
    
    def reload(self) -> None:
        """Reload the configuration from the file."""
        self._load_config()
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access to configuration."""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style setting of configuration."""
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        """Check if a configuration key exists."""
        try:
            self.get(key)
            return True
        except KeyError:
            return False
    
    def to_dict(self) -> Dict:
        """Return a deep copy of the configuration as a dictionary."""
        import copy
        return copy.deepcopy(self._config)
