"""
Logging utility for the Jetson TX1 Personal Assistant.
Provides centralized logging with file rotation and console output.
"""

import logging
import logging.handlers
import os
import sys
from typing import Optional

def setup_logger(
    name: str = 'assistant',
    level: str = 'INFO',
    log_file: Optional[str] = None,
    max_size: int = 10,  # MB
    backup_count: int = 3,
    console: bool = True
) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        max_size: Maximum log file size in MB before rotation
        backup_count: Number of backup logs to keep
        console: Whether to log to console
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Set log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(os.path.abspath(log_file))
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_size * 1024 * 1024,  # Convert MB to bytes
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Create a default logger instance
logger = setup_logger()

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name. If None, returns the root logger.
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name) if name else logging.getLogger()
