"""
Configuration Manager for VibeOBS
Handles YAML configuration loading, validation, and hot-reload monitoring.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Optional, Any


class ConfigManager:
    """Handles configuration loading and monitoring"""
    
    DEFAULT_CONFIG = {
        "obs": {
            "host": "localhost",
            "port": 4455,
            "password": ""
        },
        "app_scene_mappings": {
            "Emacs": "editor",
            "Alacritty": "terminal",
            "Chrome": "browser"
        },
        "polling_interval": 0.5,
        "log_level": "INFO",
        "log_file": "~/.config/vibeobs/vibeobs.log"
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize ConfigManager
        
        Args:
            config_path: Path to config file. Defaults to ~/.config/vibeobs/config.yaml
        """
        self.config_path = config_path or Path.home() / ".config" / "vibeobs" / "config.yaml"
        self.actual_config_path = None
        self.config_mtime = None
        self.config = {}
    
    def load(self) -> Optional[Dict[str, Any]]:
        """
        Load configuration from YAML file
        
        Returns:
            Configuration dictionary or None if loading fails
        """
        # Try local config.yaml first
        local_config_path = Path(__file__).parent / "config.yaml"
        
        for path in [local_config_path, self.config_path]:
            if path.exists():
                config = self._load_from_file(path)
                if config:
                    self.actual_config_path = path
                    self.config_mtime = path.stat().st_mtime
                    self.config = config
                    print(f"Loaded config from: {path}")
                    return config
        
        # Use defaults if no config found
        print("No config file found, using defaults")
        self.config = self.DEFAULT_CONFIG.copy()
        return self.config
    
    def _load_from_file(self, path: Path) -> Optional[Dict[str, Any]]:
        """
        Load and parse YAML file
        
        Args:
            path: Path to YAML file
            
        Returns:
            Parsed configuration or None if invalid
        """
        try:
            with open(path, 'r') as f:
                user_config = yaml.safe_load(f)
                if not user_config:
                    return None
                
                # Merge with defaults
                config = self.DEFAULT_CONFIG.copy()
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in config:
                        config[key].update(value)
                    else:
                        config[key] = value
                
                # Expand paths
                if "log_file" in config and "~" in config["log_file"]:
                    config["log_file"] = os.path.expanduser(config["log_file"])
                
                # Validate configuration
                if not self._validate_config(config):
                    return None
                
                return config
                
        except yaml.YAMLError as e:
            print(f"Error parsing YAML from {path}: {e}")
        except Exception as e:
            print(f"Error loading config from {path}: {e}")
        
        return None
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration structure
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if "obs" not in config or not isinstance(config["obs"], dict):
            print("Invalid config: 'obs' section missing or invalid")
            return False
        
        if "app_scene_mappings" not in config or not isinstance(config["app_scene_mappings"], dict):
            print("Invalid config: 'app_scene_mappings' section missing or invalid")
            return False
        
        # Validate OBS settings
        obs_config = config["obs"]
        if "host" not in obs_config or "port" not in obs_config:
            print("Invalid config: OBS host or port missing")
            return False
        
        # Validate port number
        try:
            port = int(obs_config["port"])
            if port < 1 or port > 65535:
                print(f"Invalid config: OBS port {port} out of range")
                return False
        except (ValueError, TypeError):
            print(f"Invalid config: OBS port must be a number")
            return False
        
        # Validate polling interval
        if "polling_interval" in config:
            try:
                interval = float(config["polling_interval"])
                if interval <= 0:
                    print("Invalid config: polling_interval must be positive")
                    return False
            except (ValueError, TypeError):
                print("Invalid config: polling_interval must be a number")
                return False
        
        return True
    
    def has_changed(self) -> bool:
        """
        Check if config file has been modified
        
        Returns:
            True if config file has changed, False otherwise
        """
        if not self.actual_config_path or not self.actual_config_path.exists():
            return False
        
        current_mtime = self.actual_config_path.stat().st_mtime
        return current_mtime != self.config_mtime
    
    def reload(self) -> bool:
        """
        Reload configuration if valid
        
        Returns:
            True if reload successful, False otherwise
        """
        if not self.actual_config_path:
            return False
            
        new_config = self._load_from_file(self.actual_config_path)
        if new_config:
            self.config = new_config
            self.config_mtime = self.actual_config_path.stat().st_mtime
            return True
        return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value