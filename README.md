# Jetson TX1 Personal Assistant

A sophisticated personal assistant application designed for the NVIDIA Jetson TX1 platform, providing voice-controlled assistance with a modular skill system and modern GUI.

## Features

- Voice Commands: Natural language processing for voice interactions
- Modular Skills: Easily extensible with custom skills
- Modern GUI: Clean, responsive interface with dark/light themes
- Wake Word Detection: Activate with a custom wake word
- Multi-Engine Support: Multiple speech recognition and TTS engines
- Event-Driven Architecture: Efficient communication between components
- Logging: Comprehensive logging for debugging and monitoring
- Voice command recognition using local processing
- Natural text-to-speech responses
- Customizable wake word detection
- GUI interface with status indicators
- Core assistant capabilities:
  - Weather forecasts
  - Calendar management
  - Web searches
  - Home automation control
  - News updates
  - Timer and alarm functions
  - Note taking
- Optimized for Jetson TX1's hardware capabilities

## Requirements

- NVIDIA Jetson TX1 running Ubuntu
- USB microphone
- Speakers
- Python 3.6+
- Internet connection for certain features

## Installation

1. Clone this repository to your Jetson TX1
2. Install dependencies:
   ```
   sudo apt update
   sudo apt install python3-pip portaudio19-dev python3-pyaudio espeak libespeak-dev
   pip3 install -r requirements.txt
   ```
3. Configure your assistant settings in `config.yml`
4. Run the application:
   ```
   python3 assistant.py
   ```

## Usage

1. Say your wake word (default: "Jetson")
2. Wait for the activation tone
3. Speak your command clearly
4. The assistant will process and respond to your request

## Customization

Edit the `config.yml` file to:
- Change the wake word
- Adjust sensitivity
- Configure service API keys
- Customize response styles
- Add new command patterns

## Architecture

The application follows a modular design with the following components:
- Core Engine: Manages application state and coordinates between modules
- Speech Recognition: Handles wake word detection and command processing
- Response Generator: Creates appropriate responses to user queries
- Service Connectors: Interfaces with external APIs and services
- GUI Interface: Provides visual feedback and control options

## License

MIT
