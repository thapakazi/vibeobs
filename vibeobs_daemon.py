#!/usr/bin/env python3
"""
VibeOBS Daemon - Automatic OBS Scene Switcher for macOS
Main daemon that orchestrates window monitoring and OBS scene switching.
"""

import logging
import signal
import sys
import time
from pathlib import Path
from typing import Optional

# Import modular components
from config_manager import ConfigManager
from obs_controller import OBSController
from window_monitor import WindowMonitor


class VibeOBSDaemon:
    """Main daemon orchestrator for VibeOBS"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize VibeOBS Daemon
        
        Args:
            config_path: Optional path to configuration file
        """
        self.running = True
        
        # Initialize configuration manager
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load()
        
        if not self.config:
            print("Failed to load configuration. Exiting.")
            sys.exit(1)
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize controllers
        self.obs_controller = OBSController(self.config, self.logger)
        self.window_monitor = WindowMonitor(self.logger)
        
        # Register window change callback
        self.window_monitor.register_callback(self._on_app_change)
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        
        # Statistics
        self.stats = {
            "scenes_switched": 0,
            "failed_switches": 0,
            "config_reloads": 0,
            "start_time": time.time()
        }
    
    def _setup_logging(self) -> logging.Logger:
        """
        Configure logging based on config
        
        Returns:
            Configured logger instance
        """
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        log_file = self.config.get("log_file")
        
        # Create log directory if needed
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Clear existing handlers
        logger = logging.getLogger("VibeOBS")
        logger.handlers.clear()
        logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add handlers
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Always add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def _handle_signal(self, signum, frame):
        """
        Handle shutdown signals gracefully
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self.logger.info(f"Received signal {signum}. Shutting down...")
        self.running = False
    
    def _reload_config(self) -> bool:
        """
        Reload configuration and update components
        
        Returns:
            True if reload successful, False otherwise
        """
        if not self.config_manager.reload():
            return False
        
        new_config = self.config_manager.config
        old_log_level = self.config.get("log_level")
        
        # Update OBS controller
        self.obs_controller.update_config(new_config)
        
        # Update logging if needed
        if old_log_level != new_config.get("log_level"):
            self.config = new_config
            self.logger = self._setup_logging()
            self.obs_controller.logger = self.logger
            self.window_monitor.logger = self.logger
        
        self.config = new_config
        self.stats["config_reloads"] += 1
        
        self.logger.info("Configuration reloaded successfully")
        self.logger.info(f"Monitoring apps: {list(self.config['app_scene_mappings'].keys())}")
        
        return True
    
    def _on_app_change(self, old_app: str, new_app: str):
        """
        Callback for application changes
        
        Args:
            old_app: Previous application name
            new_app: New application name
        """
        self.logger.debug(f"App changed: {old_app} → {new_app}")
        
        # Check if new app has a scene mapping
        if new_app not in self.config["app_scene_mappings"]:
            self.logger.debug(f"No scene mapping for: {new_app}")
            return
        
        scene_name = self.config["app_scene_mappings"][new_app]
        self.logger.info(f"App '{new_app}' activated, switching to scene '{scene_name}'")
        
        if self.obs_controller.switch_scene(scene_name):
            self.stats["scenes_switched"] += 1
        else:
            self.stats["failed_switches"] += 1
            self.logger.warning(f"Failed to switch to scene '{scene_name}'")
    
    def _print_startup_info(self):
        """Print startup information"""
        self.logger.info("=" * 60)
        self.logger.info("VibeOBS Daemon Started")
        self.logger.info("=" * 60)
        self.logger.info(f"Config: {self.config_manager.actual_config_path}")
        self.logger.info(f"Log Level: {self.config.get('log_level', 'INFO')}")
        self.logger.info(f"Polling Interval: {self.config.get('polling_interval', 0.5)}s")
        self.logger.info(f"OBS Host: {self.config.get('obs', {}).get('host', 'localhost')}")
        self.logger.info(f"OBS Port: {self.config.get('obs', {}).get('port', 4455)}")
        
        mappings = self.config.get('app_scene_mappings', {})
        self.logger.info(f"Monitoring {len(mappings)} applications:")
        for app, scene in mappings.items():
            self.logger.info(f"  {app} → {scene}")
        self.logger.info("=" * 60)
    
    def _print_shutdown_stats(self):
        """Print statistics on shutdown"""
        uptime = time.time() - self.stats["start_time"]
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        
        self.logger.info("=" * 60)
        self.logger.info("VibeOBS Daemon Statistics")
        self.logger.info("=" * 60)
        self.logger.info(f"Uptime: {hours}h {minutes}m {seconds}s")
        self.logger.info(f"Scenes Switched: {self.stats['scenes_switched']}")
        self.logger.info(f"Failed Switches: {self.stats['failed_switches']}")
        self.logger.info(f"Config Reloads: {self.stats['config_reloads']}")
        
        # Get additional stats from components
        obs_stats = self.obs_controller.get_stats()
        window_stats = self.window_monitor.get_stats()
        
        self.logger.info(f"OBS Connected: {obs_stats.get('connected', False)}")
        self.logger.info(f"Current Scene: {obs_stats.get('current_scene', 'Unknown')}")
        self.logger.info(f"Current App: {window_stats.get('current_app', 'Unknown')}")
        self.logger.info("=" * 60)
    
    def run(self):
        """Main daemon loop"""
        self._print_startup_info()
        
        # Initial OBS connection
        if not self.obs_controller.connect():
            self.logger.warning("Initial OBS connection failed. Will retry during operation.")
        
        # Timing variables
        last_config_check = time.time()
        config_check_interval = 2  # seconds
        
        try:
            while self.running:
                try:
                    # Check for config changes
                    if time.time() - last_config_check > config_check_interval:
                        if self.config_manager.has_changed():
                            self.logger.info("Config file changed, reloading...")
                            if not self._reload_config():
                                self.logger.error("Failed to reload config")
                        last_config_check = time.time()
                    
                    # Check for window changes
                    self.window_monitor.check_and_notify()
                    
                    # Sleep before next check
                    time.sleep(self.config.get("polling_interval", 0.5))
                    
                except KeyboardInterrupt:
                    self.logger.info("Keyboard interrupt received")
                    break
                except Exception as e:
                    self.logger.error(f"Unexpected error: {e}", exc_info=True)
                    time.sleep(1)  # Prevent rapid error loops
        
        finally:
            # Cleanup
            self.obs_controller.disconnect()
            self._print_shutdown_stats()
            self.logger.info("VibeOBS Daemon stopped")


def main():
    """Entry point for the daemon"""
    # Check for command line arguments
    config_path = None
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])
        if not config_path.exists():
            print(f"Error: Config file not found: {config_path}")
            sys.exit(1)
    
    # Create and run daemon
    daemon = VibeOBSDaemon(config_path)
    daemon.run()


if __name__ == "__main__":
    main()