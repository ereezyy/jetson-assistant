#!/usr/bin/env python3
"""
Jetson TX1 Personal Assistant
Main application file that orchestrates all components
"""

import os
import sys
import signal
import logging
import threading
import time
from typing import Optional

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Import internal modules
from core.engine import AssistantEngine
from utils.config_manager import ConfigManager
from ui.main_window import MainWindow
from utils.logger import setup_logger

# Global engine instance
engine: Optional[AssistantEngine] = None

def signal_handler(sig, frame):
    """Handle interruption signals gracefully"""
    logging.info("Shutting down assistant...")
    if engine:
        engine.stop()
    sys.exit(0)

def setup_application(config: ConfigManager) -> None:
    """
    Set up and run the application with the given configuration.
    
    Args:
        config: Configuration manager instance
    """
    global engine
    
    # Setup logging
    log_config = config.get("logging", {})
    setup_logger(
        level=log_config.get("level", "INFO"),
        log_file=log_config.get("file", "assistant.log"),
        max_size=log_config.get("max_size", 10),
        backup_count=log_config.get("backup_count", 3)
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Jetson TX1 Personal Assistant")
    
    try:
        # Initialize the core engine
        engine = AssistantEngine(config)
        
        # Start the engine in a separate thread
        engine_thread = threading.Thread(target=engine.start, daemon=True)
        engine_thread.start()
        
        # Initialize the GUI if enabled
        gui_config = config.get("gui", {})
        if gui_config.get("enabled", True):
            app = QApplication(sys.argv)
            app.setApplicationName("Jetson TX1 Assistant")
            app.setApplicationDisplayName("Jetson TX1 Assistant")
            
            # Create and show the main window
            window = MainWindow(engine, config)
            window.show()
            
            # Set always on top if configured
            if gui_config.get("always_on_top", False):
                window.setWindowFlag(Qt.WindowStaysOnTopHint)
            
            # Start minimized if configured
            if gui_config.get("start_minimized", False):
                window.showMinimized()
            
            # Start the GUI event loop
            sys.exit(app.exec_())
        else:
            # If GUI is disabled, just keep the main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                signal_handler(None, None)
    
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yml")
    config = ConfigManager(config_path)
    
    # Setup and run the application
    setup_application(config)
