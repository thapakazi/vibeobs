# VibeOBS - Automatic OBS Scene Switcher

A macOS background daemon that automatically switches OBS scenes based on the currently focused application.

**Linux support next.**

## Features

- 🎬 **Automatic Scene Switching** - Switches OBS scenes when you change applications
- 🔄 **Hot Reload Configuration** - Automatically reloads when config.yaml changes (no restart needed!)
- 🔌 **Auto-Reconnect** - Reconnects to OBS if connection is lost
- 📝 **YAML Configuration** - Simple, readable configuration format
- 🐍 **Virtual Environment Support** - Works with system Python or uv/venv
- 🔍 **Comprehensive Logging** - Detailed logs for debugging
- 🚀 **Background Daemon** - Runs automatically on login using macOS launchd

## Architecture

The daemon is built with a clean, modular architecture with separate Python modules:

### Core Modules

- **`config_manager.py`** - Configuration management
  - YAML configuration loading and validation
  - Hot-reload monitoring with file change detection
  - Configuration merging with defaults
  - Path expansion and validation

- **`obs_controller.py`** - OBS WebSocket controller
  - WebSocket connection management
  - Scene switching with validation
  - Auto-reconnection logic
  - Connection statistics tracking

- **`window_monitor.py`** - macOS window monitor
  - Active application detection using PyObjC
  - Application change callbacks
  - App history tracking
  - Statistics and monitoring

- **`vibeobs_daemon.py`** - Main daemon orchestrator
  - Component initialization and coordination
  - Signal handling for graceful shutdown
  - Statistics tracking and reporting
  - Main event loop management

## Prerequisites

- **macOS** or **Linux** (Windows support planned)
- Python 3.8 or higher
- OBS Studio 28.0+ (includes WebSocket server by default)

### Platform-Specific Requirements

**macOS:**
- PyObjC (automatically installed via requirements.txt)

**Linux:**
- psutil (automatically installed via requirements.txt)
- Optional: xdotool, wmctrl, or xprop for better window detection
- For Wayland: compositor-specific tools (swaymsg, hyprctl, etc.)

## Quick Start

### 1. Clone or Download

```bash
git clone https://github.com/yourusername/vibeobs.git
cd vibeobs
```

### 2. Set up Python Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure OBS

1. Open OBS Studio
2. Go to **Tools → WebSocket Server Settings**
3. Enable **Enable WebSocket server**
4. Note the port (default: 4455) and set a password
5. Update `config.yaml` with your OBS connection details

### 4. Run the Daemon

```bash
source .venv/bin/activate
python vibeobs_daemon.py
```

## Configuration

Edit `config.yaml` to customize your setup:

```yaml
obs:
  host: 192.168.8.187  # Use localhost or IP for remote OBS
  port: 4455
  password: YourPasswordHere

app_scene_mappings:
  Emacs: editor-focused
  Alacritty: terminal-f
  Google Chrome: browser-focused
  Safari: browser-focused
  Terminal: terminal-f
  iTerm: terminal-f
  Code: editor-focused
  Visual Studio Code: editor-focused
  Slack: entire-screen
  Discord: entire-screen
  Zoom: entire-screen
  Finder: entire-screen

polling_interval: 0.5  # Seconds between checks
log_level: INFO  # DEBUG, INFO, WARNING, ERROR
log_file: ~/.config/vibeobs/vibeobs.log
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `obs.host` | OBS WebSocket server address | localhost |
| `obs.port` | WebSocket server port | 4455 |
| `obs.password` | WebSocket server password | (empty) |
| `app_scene_mappings` | Map application names to OBS scene names | See example |
| `polling_interval` | How often to check for window changes (seconds) | 0.5 |
| `log_level` | Logging verbosity | INFO |
| `log_file` | Path to log file | ~/.config/vibeobs/vibeobs.log |

### Hot Reload

The daemon automatically detects changes to `config.yaml` and reloads without needing a restart. This means you can:
- Add new application mappings
- Change OBS connection settings
- Adjust polling intervals
- Change log levels

All changes take effect within 2 seconds!

## Usage

### Managing the Daemon

**Start:**
```bash
source .venv/bin/activate
python vibeobs_daemon.py
```

**Stop:**
```bash
# Press Ctrl+C in the terminal running the daemon
```

**View Logs:**
```bash
# Logs are displayed in the terminal where daemon is running
# Or check the log file (if configured)
tail -f ~/.config/vibeobs/vibeobs.log
```

## Creating OBS Scenes

Set up your OBS scenes to match the names in your config:

1. **Common Scene Names:**
   - `editor-focused` - For coding/text editing
   - `terminal-f` - For terminal/command line
   - `browser-focused` - For web browsing
   - `entire-screen` - For general desktop/communication
   - `meeting` - For video calls

2. **Configure Each Scene:**
   - Add appropriate sources (Window Capture, Display Capture)
   - Configure audio sources
   - Add overlays, webcam, etc.

## Testing

Test the connection and scene switching:

```bash
# Test OBS connection
python tests/test_obs_connection.py

# Test individual components
python tests/debug_components.py

# Test daemon switching behavior
python tests/test_daemon_switching.py
```

## Troubleshooting

### Daemon Won't Start
- Check Python installation: `which python3`
- Verify dependencies: `pip3 list | grep -E "PyObjC|obs-websocket|PyYAML"`
- Check error logs: `cat ~/.config/vibeobs/stderr.log`

### Can't Connect to OBS
- Ensure OBS WebSocket server is enabled (Tools → WebSocket Server Settings)
- Verify port and password in `config.yaml`
- Check firewall settings if using remote OBS
- Test connection: `telnet localhost 4455`

### Scene Not Switching
- Verify scene names match exactly (case-sensitive)
- Check app names in Activity Monitor match your config
- Review logs for warnings: `tail -f ~/.config/vibeobs/vibeobs.log`
- Ensure the application has focus (not just visible)

### Config Changes Not Applied
- Check YAML syntax: `python -c "import yaml; yaml.safe_load(open('config.yaml'))"`
- Look for reload messages in logs
- Invalid YAML will be rejected, keeping the previous config

### High CPU Usage
- Increase `polling_interval` in config.yaml (e.g., 1.0 or 2.0 seconds)
- Check logs for rapid reconnection attempts

## File Structure

```
vibeobs/
├── vibeobs_daemon.py        # Main daemon orchestrator
├── config_manager.py        # Configuration loading and hot-reload
├── obs_controller.py        # OBS WebSocket connection management
├── window_monitor.py        # Cross-platform window focus monitoring
├── __init__.py             # Package initialization
├── config.yaml             # Configuration file (YAML format)
├── requirements.txt        # Python dependencies
├── tests/                  # Test scripts and utilities
│   ├── test_obs_connection.py    # OBS connection tester
│   ├── debug_components.py       # Component debugging tool
│   └── test_daemon_switching.py  # Daemon switching test
└── README.md               # This file
```

## Privacy & Security

- Only reads window focus information (no window content)
- All data stays local on your machine
- OBS connection secured with password authentication
- No network requests except to OBS

## Requirements

- **Python Libraries:**
  - PyObjC >= 9.0 (macOS integration)
  - obs-websocket-py >= 1.0 (OBS control)
  - PyYAML >= 6.0 (configuration)

- **System Requirements:**
  - macOS 12.0+ or Linux (Ubuntu 20.04+, Fedora 35+, etc.)
  - Python 3.8 or higher
  - OBS Studio 28.0 or higher

## Development

The daemon is structured with clean separation of concerns across multiple modules:

### Module Overview

```python
# Import individual components
from config_manager import ConfigManager
from obs_controller import OBSController
from window_monitor import WindowMonitor
from vibeobs_daemon import VibeOBSDaemon

# Or import as a package
import vibeobs
```

### Key Classes and Methods

**ConfigManager:**
- `load()` - Load configuration from YAML
- `reload()` - Reload configuration if changed
- `has_changed()` - Check if config file modified
- `get(key, default)` - Get config value with dot notation

**OBSController:**
- `connect()` - Connect to OBS WebSocket
- `switch_scene(scene_name)` - Switch to specific scene
- `get_current_scene()` - Get current scene name
- `get_stats()` - Get connection statistics

**WindowMonitor:**
- `get_active_app()` - Get current active application
- `check_and_notify()` - Check for changes and trigger callbacks
- `register_callback(func)` - Register app change callback
- `get_stats()` - Get monitoring statistics

### Extending the Daemon

To add new features:

1. **New Scene Switching Logic:**
   ```python
   # In window_monitor.py, add custom detection
   def get_active_app_info(self):
       # Returns detailed app information
   ```

2. **Custom Callbacks:**
   ```python
   # Register custom callbacks for app changes
   monitor.register_callback(my_custom_handler)
   ```

3. **Additional Configuration:**
   ```python
   # Add to DEFAULT_CONFIG in config_manager.py
   "my_feature": {"enabled": True}
   ```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes (maintain the modular structure)
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

### Testing

Run individual modules:
```bash
# Test configuration loading
python -c "from config_manager import ConfigManager; cm = ConfigManager(); print(cm.load())"

# Test window monitoring
python -c "from window_monitor import WindowMonitor; import logging; wm = WindowMonitor(logging.getLogger()); print(wm.get_active_app())"

# Run with custom config
python vibeobs_daemon.py /path/to/custom/config.yaml

# Run comprehensive component tests
python tests/debug_components.py
```

## License

MIT License - Feel free to modify and distribute

## Acknowledgments

- Built with PyObjC for macOS integration
- Uses obs-websocket-py for OBS control
- Inspired by the streaming community's need for automation
- Thanks to the OBS Project for the excellent WebSocket API

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the logs for detailed error information
- Ensure you're using the latest version

---

**Note:** This tool is designed specifically for macOS. For Windows or Linux alternatives, consider using OBS's built-in automation features or platform-specific window managers.
