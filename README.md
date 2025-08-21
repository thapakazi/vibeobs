# VibeOBS - Automatic OBS Scene Switcher

A macOS background daemon that automatically switches OBS scenes based on the currently focused application.

## Features

- 🎬 Automatically switches OBS scenes when you change applications
- 🔄 Runs as a background daemon using macOS launchd
- ⚙️ Configurable app-to-scene mappings
- 📝 Comprehensive logging for debugging
- 🔌 Reconnects automatically to OBS if connection is lost
- 🐍 Supports both system Python and uv virtual environments

## Prerequisites

- macOS (tested on macOS 12+)
- Python 3.8 or higher
- OBS Studio 28.0+ (includes WebSocket server by default)

## Quick Start

### 1. Clone or Download

```bash
git clone https://github.com/yourusername/vibeobs.git
cd vibeobs
```

### 2. Set up Python Environment (Optional)

If using uv for Python management:

```bash
uv venv
source .venv/bin/activate
```

### 3. Configure OBS

1. Open OBS Studio
2. Go to **Tools → WebSocket Server Settings**
3. Enable **Enable WebSocket server**
4. Note the port (default: 4455) and password
5. Update `config.json` with your OBS connection details

### 4. Install and Run

```bash
chmod +x install.sh uninstall.sh
./install.sh
```

The installer will:
- Install Python dependencies (PyObjC, obs-websocket-py)
- Set up configuration files
- Install and start the launchd daemon
- The daemon will start automatically on login

## Configuration

Edit `~/.config/vibeobs/config.json` to customize:

```json
{
  "obs": {
    "host": "localhost",
    "port": 4455,
    "password": "your-password-here"
  },
  "app_scene_mappings": {
    "Emacs": "editor",
    "Alacritty": "terminal",
    "Safari": "browser",
    "Chrome": "browser",
    "Code": "editor",
    "Terminal": "terminal",
    "Slack": "communication",
    "Zoom": "meeting"
  },
  "polling_interval": 0.5,
  "log_level": "INFO"
}
```

### Configuration Options

- **obs.host**: OBS WebSocket server address (use IP for remote OBS)
- **obs.port**: WebSocket server port (default: 4455)
- **obs.password**: WebSocket server password
- **app_scene_mappings**: Map application names to OBS scene names
- **polling_interval**: How often to check for window focus changes (seconds)
- **log_level**: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

## Usage

### Start the Daemon
```bash
./install.sh
```

### Stop the Daemon
```bash
./uninstall.sh
```

### View Logs
```bash
# Main log
tail -f ~/.config/vibeobs/vibeobs.log

# Error log
tail -f ~/.config/vibeobs/stderr.log
```

### Manual Control
```bash
# Check if daemon is running
launchctl list | grep vibeobs

# Stop manually
launchctl unload ~/Library/LaunchAgents/com.vibeobs.daemon.plist

# Start manually
launchctl load ~/Library/LaunchAgents/com.vibeobs.daemon.plist
```

## Creating OBS Scenes

1. In OBS, create scenes matching the names in your config:
   - `editor` - For coding/text editing
   - `terminal` - For terminal/command line
   - `browser` - For web browsing
   - `communication` - For Slack/Discord
   - `meeting` - For video calls
   - `desktop` - For general desktop

2. Configure each scene with appropriate sources:
   - Window Capture
   - Display Capture
   - Audio sources
   - Overlays/webcam

## Troubleshooting

### Daemon won't start
- Check Python installation: `which python3`
- Verify dependencies: `pip3 list | grep -E "PyObjC|obs-websocket"`
- Check logs: `cat ~/.config/vibeobs/stderr.log`

### Can't connect to OBS
- Ensure OBS WebSocket server is enabled
- Verify port and password in config.json
- Check firewall settings if using remote OBS
- Test connection: `telnet localhost 4455`

### Scene not switching
- Verify scene names match exactly (case-sensitive)
- Check app names in Activity Monitor match config
- Review logs for warnings about missing scenes
- Ensure the app has focus (not just visible)

### High CPU usage
- Increase `polling_interval` in config.json (e.g., 1.0 or 2.0)
- Check for errors causing rapid reconnection attempts

## File Structure

```
vibeobs/
├── vibeobs_daemon.py      # Main daemon script
├── config.json            # Configuration template
├── requirements.txt       # Python dependencies
├── install.sh            # Installation script
├── uninstall.sh         # Uninstallation script
├── com.vibeobs.daemon.plist  # launchd configuration
└── README.md            # This file
```

## Privacy & Security

- The daemon only reads window focus information
- No window content is accessed or recorded
- All data stays local on your machine
- OBS connection can be secured with password

## License

MIT License - Feel free to modify and distribute

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

## Acknowledgments

- Uses PyObjC for macOS integration
- Uses obs-websocket-py for OBS control
- Inspired by the streaming community's need for automation