#!/usr/bin/env python3

import yaml
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from AppKit import NSWorkspace
except ImportError:
    print("Can't import AppKit -- Install with: pip install PyObjC")
    sys.exit(1)

try:
    from obswebsocket import obsws, requests
except ImportError:
    print("Can't import obswebsocket -- Install with: pip install obs-websocket-py")
    sys.exit(1)


class VibeOBSDaemon:
    def __init__(self, config_path=None):
        self.running = True
        self.config_path = config_path or Path.home() / ".config" / "vibeobs" / "config.yaml"
        self.config = {}
        self.actual_config_path = None
        self.config_mtime = None
        self.load_and_apply_config()
        self.obs_client = None
        self.last_active_app = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)

    def load_and_apply_config(self):
        """Load configuration and apply settings"""
        new_config = self.load_config()
        if new_config:
            old_config = self.config
            self.config = new_config
            
            # Update config modification time
            if self.actual_config_path and self.actual_config_path.exists():
                self.config_mtime = self.actual_config_path.stat().st_mtime
            
            # Setup or reconfigure logging if needed
            if not hasattr(self, 'logger') or old_config.get('log_level') != new_config.get('log_level'):
                self.setup_logging()
                if hasattr(self, 'logger'):
                    self.logger.info("Configuration reloaded successfully")
            
            # Disconnect OBS client if connection settings changed
            if old_config and self.obs_client:
                old_obs = old_config.get('obs', {})
                new_obs = new_config.get('obs', {})
                if (old_obs.get('host') != new_obs.get('host') or 
                    old_obs.get('port') != new_obs.get('port') or
                    old_obs.get('password') != new_obs.get('password')):
                    try:
                        self.obs_client.disconnect()
                        self.obs_client = None
                        if hasattr(self, 'logger'):
                            self.logger.info("OBS connection settings changed, disconnected from OBS")
                    except:
                        pass
            
            return True
        return False

    def load_config(self):
        """Load configuration from YAML file or use defaults"""
        default_config = {
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
            "log_file": str(Path.home() / ".config" / "vibeobs" / "vibeobs.log")
        }
        
        # First try local config.yaml in the same directory
        local_config_path = Path(__file__).parent / "config.yaml"
        config_to_use = None
        
        if local_config_path.exists():
            try:
                with open(local_config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:  # Check if YAML is valid and not empty
                        # Merge user config with defaults
                        for key, value in user_config.items():
                            if isinstance(value, dict) and key in default_config:
                                default_config[key].update(value)
                            else:
                                default_config[key] = value
                        self.actual_config_path = local_config_path
                        print(f"Loaded config from: {local_config_path}")
                        config_to_use = default_config
            except yaml.YAMLError as e:
                print(f"Error parsing YAML from {local_config_path}: {e}")
                return None
            except Exception as e:
                print(f"Error loading local config: {e}")
                return None
        
        # Then check the user config path
        elif self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:  # Check if YAML is valid and not empty
                        # Merge user config with defaults
                        for key, value in user_config.items():
                            if isinstance(value, dict) and key in default_config:
                                default_config[key].update(value)
                            else:
                                default_config[key] = value
                        self.actual_config_path = self.config_path
                        print(f"Loaded config from: {self.config_path}")
                        config_to_use = default_config
            except yaml.YAMLError as e:
                print(f"Error parsing YAML from {self.config_path}: {e}")
                return None
            except Exception as e:
                print(f"Error loading config: {e}")
                return None
        
        # If no config file found, use defaults
        if config_to_use is None:
            print("No config file found, using defaults")
            config_to_use = default_config
        
        return config_to_use

    def check_config_changes(self):
        """Check if config file has been modified and reload if valid"""
        if self.actual_config_path and self.actual_config_path.exists():
            current_mtime = self.actual_config_path.stat().st_mtime
            if current_mtime != self.config_mtime:
                self.logger.info(f"Config file changed, attempting to reload...")
                
                # Try to load the new config
                if self.load_and_apply_config():
                    self.logger.info(f"Config reloaded successfully from {self.actual_config_path}")
                    self.logger.info(f"Monitoring applications: {list(self.config['app_scene_mappings'].keys())}")
                else:
                    self.logger.error("Failed to reload config - keeping previous configuration")

    def setup_logging(self):
        """Configure logging based on config settings"""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        log_file = self.config.get("log_file")
        
        # Expand ~ in path
        if log_file and "~" in log_file:
            log_file = os.path.expanduser(log_file)
        
        # Create log directory if it doesn't exist
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Clear existing handlers
        logger = logging.getLogger("VibeOBS")
        logger.handlers.clear()
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file) if log_file else logging.StreamHandler(),
                logging.StreamHandler()  # Also log to console
            ]
        )
        self.logger = logging.getLogger("VibeOBS")

    def handle_signal(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}. Shutting down...")
        self.running = False

    def connect_to_obs(self):
        """Connect to OBS WebSocket server"""
        try:
            obs_config = self.config["obs"]
            self.obs_client = obsws(
                obs_config["host"],
                obs_config["port"],
                obs_config.get("password", "")
            )
            self.obs_client.connect()
            self.logger.info(f"Connected to OBS at {obs_config['host']}:{obs_config['port']}")
            self.reconnect_attempts = 0
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to OBS: {e}")
            self.obs_client = None
            return False

    def switch_scene(self, scene_name):
        """Switch to the specified OBS scene"""
        if not self.obs_client:
            if not self.connect_to_obs():
                return False
        
        try:
            # First get the list of available scenes to validate
            scenes = self.obs_client.call(requests.GetSceneList())
            available_scenes = [s['sceneName'] for s in scenes.getScenes()]
            
            if scene_name not in available_scenes:
                self.logger.warning(f"Scene '{scene_name}' not found. Available scenes: {available_scenes}")
                return False
            
            # Switch to the scene
            self.obs_client.call(requests.SetCurrentProgramScene(sceneName=scene_name))
            self.logger.info(f"Switched to scene: {scene_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error switching scene: {e}")
            # Try to reconnect on next attempt
            self.obs_client = None
            return False

    def get_active_app_name(self):
        """Get the name of the currently active application"""
        try:
            active_app = NSWorkspace.sharedWorkspace().activeApplication()
            return active_app['NSApplicationName']
        except Exception as e:
            self.logger.error(f"Error getting active application: {e}")
            return None

    def run(self):
        """Main daemon loop"""
        self.logger.info("VibeOBS Daemon started")
        self.logger.info(f"Config file: {self.actual_config_path}")
        self.logger.info(f"Monitoring applications: {list(self.config['app_scene_mappings'].keys())}")
        
        # Initial OBS connection
        if not self.connect_to_obs():
            self.logger.warning("Initial OBS connection failed. Will retry during operation.")
        
        last_config_check = time.time()
        config_check_interval = 2  # Check config every 2 seconds
        
        while self.running:
            try:
                # Check for config file changes periodically
                if time.time() - last_config_check > config_check_interval:
                    self.check_config_changes()
                    last_config_check = time.time()
                
                current_app = self.get_active_app_name()
                
                if current_app and current_app != self.last_active_app:
                    self.logger.debug(f"Active app changed: {self.last_active_app} -> {current_app}")
                    self.last_active_app = current_app
                    
                    # Check if this app has a scene mapping
                    if current_app in self.config["app_scene_mappings"]:
                        scene_name = self.config["app_scene_mappings"][current_app]
                        self.logger.info(f"App '{current_app}' activated, switching to scene '{scene_name}'")
                        
                        if not self.switch_scene(scene_name):
                            self.reconnect_attempts += 1
                            if self.reconnect_attempts >= self.max_reconnect_attempts:
                                self.logger.error(f"Max reconnection attempts ({self.max_reconnect_attempts}) reached. Continuing without OBS.")
                    else:
                        self.logger.debug(f"No scene mapping for app: {current_app}")
                
                time.sleep(self.config["polling_interval"])
                
            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in main loop: {e}")
                time.sleep(1)  # Prevent rapid error loops
        
        # Cleanup
        if self.obs_client:
            try:
                self.obs_client.disconnect()
                self.logger.info("Disconnected from OBS")
            except:
                pass
        
        self.logger.info("VibeOBS Daemon stopped")


def main():
    """Entry point for the daemon"""
    daemon = VibeOBSDaemon()
    daemon.run()


if __name__ == "__main__":
    main()
