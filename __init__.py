"""
VibeOBS - Automatic OBS Scene Switcher for macOS
A modular daemon for automatically switching OBS scenes based on active applications.
"""

__version__ = "1.0.0"
__author__ = "VibeOBS Contributors"
__license__ = "MIT"

from .config_manager import ConfigManager
from .obs_controller import OBSController
from .window_monitor import WindowMonitor
from .vibeobs_daemon import VibeOBSDaemon

__all__ = [
    "ConfigManager",
    "OBSController",
    "WindowMonitor",
    "VibeOBSDaemon",
]