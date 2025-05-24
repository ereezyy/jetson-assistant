#!/usr/bin/env python3
"""
Main Window for the Jetson TX1 Personal Assistant
Provides GUI interface for the assistant
"""

import os
import sys
import time
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QTextEdit, QProgressBar,
                            QSystemTrayIcon, QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap


class MainWindow(QMainWindow):
    """Main window for the personal assistant GUI"""
    
    def __init__(self, engine, config):
        """
        Initialize the main window
        
        Args:
            engine: AssistantEngine instance
            config: ConfigManager instance
        """
        super().__init__()
        
        self.engine = engine
        self.config = config
        
        # Set up the UI
        self.setup_ui()
        
        # Connect to events
        self.connect_events()
        
        logging.info("GUI initialized")
    
    def setup_ui(self):
        """Set up the user interface"""
        # Set window properties
        self.setWindowTitle("Jetson TX1 Personal Assistant")
        self.setMinimumSize(600, 400)
        
        # Set theme
        self.set_theme(self.config.get("gui.theme", "dark"))
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        # Add logo/status area
        self.setup_header()
        
        # Add conversation display
        self.setup_conversation_display()
        
        # Add status bar
        self.setup_status_bar()
        
        # Set up system tray
        self.setup_system_tray()
        
        # Set up timers
        self.setup_timers()
    
    def setup_header(self):
        """Set up the header with logo and status"""
        header_layout = QHBoxLayout()
        
        # Logo label
        self.logo_label = QLabel()
        self.logo_label.setMaximumSize(64, 64)
        self.logo_label.setMinimumSize(64, 64)
        
        # Load logo if exists, otherwise show text
        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "resources", "logo.png"
        )
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            self.logo_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.logo_label.setText("Jetson\nAssistant")
            self.logo_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(self.logo_label)
        
        # Status and controls
        status_layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        status_layout.addWidget(self.status_label)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        # Activate button
        self.activate_button = QPushButton("Activate")
        self.activate_button.clicked.connect(self.on_activate_clicked)
        control_layout.addWidget(self.activate_button)
        
        # Mute button
        self.mute_button = QPushButton("Mute")
        self.mute_button.setCheckable(True)
        self.mute_button.clicked.connect(self.on_mute_clicked)
        control_layout.addWidget(self.mute_button)
        
        # Settings button
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.on_settings_clicked)
        control_layout.addWidget(self.settings_button)
        
        status_layout.addLayout(control_layout)
        header_layout.addLayout(status_layout)
        
        self.main_layout.addLayout(header_layout)
    
    def setup_conversation_display(self):
        """Set up the conversation display area"""
        # Conversation history
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.conversation_display.setMinimumHeight(200)
        self.main_layout.addWidget(self.conversation_display)
        
        # Add welcome message
        self.add_assistant_message("Welcome to your Jetson TX1 Personal Assistant. Say the wake word or press Activate to begin.")
        
        # Voice activity indicator
        activity_layout = QHBoxLayout()
        
        self.activity_label = QLabel("Voice Activity:")
        activity_layout.addWidget(self.activity_label)
        
        self.activity_bar = QProgressBar()
        self.activity_bar.setMaximum(100)
        self.activity_bar.setValue(0)
        self.activity_bar.setTextVisible(False)
        self.activity_bar.setMaximumHeight(15)
        activity_layout.addWidget(self.activity_bar)
        
        self.main_layout.addLayout(activity_layout)
    
    def setup_status_bar(self):
        """Set up the status bar"""
        self.statusBar().showMessage("Ready")
        
        # Add permanent widgets
        self.wake_word_label = QLabel(f"Wake Word: {self.config.get('wake_word.word', 'Jetson')}")
        self.statusBar().addPermanentWidget(self.wake_word_label)
        
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: green;")
        self.statusBar().addPermanentWidget(self.status_indicator)
    
    def setup_system_tray(self):
        """Set up system tray icon and menu"""
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Load icon if exists, otherwise use system default
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "resources", "icon.png"
        )
        
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.on_quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Connect signals
        self.tray_icon.activated.connect(self.on_tray_activated)
    
    def setup_timers(self):
        """Set up timers for UI updates"""
        # Activity update timer
        self.activity_timer = QTimer(self)
        self.activity_timer.timeout.connect(self.update_activity_indicator)
        self.activity_timer.start(100)  # Update every 100ms
    
    def set_theme(self, theme):
        """
        Set the application theme
        
        Args:
            theme (str): Theme name (dark or light)
        """
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2D2D30;
                    color: #FFFFFF;
                }
                QLabel {
                    color: #FFFFFF;
                }
                QPushButton {
                    background-color: #3E3E42;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
                QPushButton:pressed {
                    background-color: #007ACC;
                }
                QTextEdit {
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                    border: 1px solid #3E3E42;
                }
                QProgressBar {
                    border: 1px solid #3E3E42;
                    border-radius: 3px;
                    background-color: #1E1E1E;
                }
                QProgressBar::chunk {
                    background-color: #007ACC;
                    width: 1px;
                }
            """)
        else:  # Light theme
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #F0F0F0;
                    color: #000000;
                }
                QLabel {
                    color: #000000;
                }
                QPushButton {
                    background-color: #E0E0E0;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #CCCCCC;
                }
                QPushButton:pressed {
                    background-color: #007ACC;
                    color: #FFFFFF;
                }
                QTextEdit {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                }
                QProgressBar {
                    border: 1px solid #CCCCCC;
                    border-radius: 3px;
                    background-color: #FFFFFF;
                }
                QProgressBar::chunk {
                    background-color: #007ACC;
                    width: 1px;
                }
            """)
    
    def connect_events(self):
        """Connect to engine events"""
        from utils.event_bus import EventBus
        event_bus = EventBus()
        
        # Connect to assistant events
        event_bus.subscribe("assistant_activated", self.on_assistant_activated)
        event_bus.subscribe("assistant_deactivated", self.on_assistant_deactivated)
        event_bus.subscribe("wake_word_detected", self.on_wake_word_detected)
        event_bus.subscribe("speech_recognized", self.on_speech_recognized)
        event_bus.subscribe("command_processed", self.on_command_processed)
        event_bus.subscribe("error", self.on_error)
    
    def on_assistant_activated(self, event_data):
        """
        Handler for assistant activation event
        
        Args:
            event_data: Event data
        """
        self.status_label.setText("Active - Listening")
        self.status_indicator.setStyleSheet("color: blue;")
        self.statusBar().showMessage("Listening for command...")
    
    def on_assistant_deactivated(self, event_data):
        """
        Handler for assistant deactivation event
        
        Args:
            event_data: Event data
        """
        self.status_label.setText("Ready")
        self.status_indicator.setStyleSheet("color: green;")
        self.statusBar().showMessage("Ready")
    
    def on_wake_word_detected(self, event_data):
        """
        Handler for wake word detection event
        
        Args:
            event_data: Event data
        """
        self.add_system_message(f"Wake word detected")
    
    def on_speech_recognized(self, event_data):
        """
        Handler for speech recognition event
        
        Args:
            event_data: Event data
        """
        text = event_data.get("text", "")
        if text:
            self.add_user_message(text)
    
    def on_command_processed(self, event_data):
        """
        Handler for command processed event
        
        Args:
            event_data: Event data
        """
        response = event_data.get("response", "")
        if response:
            self.add_assistant_message(response)
    
    def on_error(self, event_data):
        """
        Handler for error event
        
        Args:
            event_data: Event data
        """
        message = event_data.get("message", "Unknown error")
        source = event_data.get("source", "unknown")
        
        self.add_system_message(f"Error in {source}: {message}")
        self.status_indicator.setStyleSheet("color: red;")
        
        # Reset to green after 3 seconds
        QTimer.singleShot(3000, lambda: self.status_indicator.setStyleSheet("color: green;"))
    
    def add_user_message(self, message):
        """
        Add a user message to the conversation display
        
        Args:
            message (str): Message to add
        """
        self.conversation_display.append(f'<p style="margin-top:0px; margin-bottom:0px;"><b>You:</b> {message}</p>')
        self.conversation_display.ensureCursorVisible()
    
    def add_assistant_message(self, message):
        """
        Add an assistant message to the conversation display
        
        Args:
            message (str): Message to add
        """
        self.conversation_display.append(f'<p style="margin-top:0px; margin-bottom:0px;"><b>Assistant:</b> {message}</p>')
        self.conversation_display.ensureCursorVisible()
    
    def add_system_message(self, message):
        """
        Add a system message to the conversation display
        
        Args:
            message (str): Message to add
        """
        self.conversation_display.append(f'<p style="margin-top:0px; margin-bottom:0px; color: #888888;"><i>System: {message}</i></p>')
        self.conversation_display.ensureCursorVisible()
    
    def update_activity_indicator(self):
        """Update the voice activity indicator"""
        # This would be connected to audio levels in a real implementation
        # For now, just simulate some activity when the assistant is active
        if self.engine.active:
            # Simulate audio activity
            import random
            level = random.randint(0, 100)
            self.activity_bar.setValue(level)
        else:
            self.activity_bar.setValue(0)
    
    def on_activate_clicked(self):
        """Handler for activate button click"""
        from utils.event_bus import EventBus
        EventBus().publish("wake_word_detected", {"source": "button"})
    
    def on_mute_clicked(self):
        """Handler for mute button click"""
        if self.mute_button.isChecked():
            self.add_system_message("Assistant muted")
            self.mute_button.setText("Unmute")
            # TODO: Implement muting in the engine
        else:
            self.add_system_message("Assistant unmuted")
            self.mute_button.setText("Mute")
            # TODO: Implement unmuting in the engine
    
    def on_settings_clicked(self):
        """Handler for settings button click"""
        # TODO: Implement settings dialog
        QMessageBox.information(self, "Settings", "Settings dialog not implemented yet")
    
    def on_tray_activated(self, reason):
        """
        Handler for tray icon activation
        
        Args:
            reason: Activation reason
        """
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()
    
    def on_quit(self):
        """Handler for quit action"""
        # Shutdown the engine
        self.engine.shutdown()
        
        # Quit the application
        import sys
        sys.exit(0)
    
    def closeEvent(self, event):
        """
        Override close event to minimize to tray instead
        
        Args:
            event: Close event
        """
        if self.config.get("gui.minimize_to_tray_on_close", True):
            event.ignore()
            self.hide()
            
            # Show notification
            self.tray_icon.showMessage(
                "Jetson TX1 Assistant",
                "The assistant is still running in the background",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            # Shutdown the engine
            self.engine.shutdown()
            event.accept()
