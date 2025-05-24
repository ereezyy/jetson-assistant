# Jetson TX1 Personal Assistant

A sophisticated personal assistant application designed for the NVIDIA Jetson TX1 platform, providing voice-controlled assistance with a modular skill system and modern GUI.

## ✨ Features

- 🎙️ **Voice Commands**: Natural language processing for voice interactions
- 🧩 **Modular Skills**: Easily extensible with custom skills
- 🖥️ **Modern GUI**: Clean, responsive interface with dark/light themes
- 🎯 **Wake Word Detection**: Activate with a custom wake word
- 🗣️ **Multi-Engine Support**: Multiple speech recognition and TTS engines
- ⚡ **Event-Driven Architecture**: Efficient communication between components
- 📝 **Logging**: Comprehensive logging for debugging and monitoring

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- NVIDIA Jetson TX1 with JetPack 4.6.1 or later
- PulseAudio or ALSA for audio
- Internet connection (for online services)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ereezyy/jetson-assistant.git
   cd jetson-assistant
   ```

2. **Create and activate a virtual environment (recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note for Jetson TX1**: Some packages might need to be installed via `apt` first:
   ```bash
   sudo apt-get update
   sudo apt-get install portaudio19-dev python3-pyaudio
   ```

4. **Configure the assistant**:
   - Edit `config.yml` to customize settings
   - Add API keys for online services if needed

## 🏃‍♂️ Usage

### Starting the Assistant

```bash
python assistant.py
```

### Command Line Options

- `--config PATH`: Specify a custom config file (default: `config.yml`)
- `--no-gui`: Run in console-only mode
- `--debug`: Enable debug logging

### Basic Commands

- "Jetson, what time is it?" - Get the current time
- "Jetson, what's today's date?" - Get today's date
- "Jetson, what day is it?" - Get the current day of the week
- "Jetson, time in New York" - Get the current time in another location

## 🛠️ Development

### Project Structure

```
jetson-assistant/
├── core/                  # Core functionality
│   ├── engine.py          # Main engine
│   ├── skills/            # Built-in skills
│   └── ...
├── ui/                    # User interface
│   └── main_window.py     # Main application window
├── utils/                 # Utility modules
│   ├── config_manager.py  # Configuration handling
│   ├── event_bus.py       # Event system
│   └── logger.py          # Logging utilities
├── config.yml             # Configuration file
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

### Creating a New Skill

1. Create a new Python file in `core/skills/`
2. Create a class that inherits from `Skill`
3. Implement the required methods and add intent handlers

Example skill (`core/skills/example.py`):

```python
from core.skills.base_skill import Skill, intent

class ExampleSkill(Skill):
    @property
    def name(self):
        return "example"
    
    @intent("say hello")
    async def handle_hello(self):
        return "Hello! How can I help you today?"
```

### Testing

Run tests with pytest:

```bash
pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) before submitting pull requests.

## 📧 Contact

For questions or support, please open an issue on GitHub.
