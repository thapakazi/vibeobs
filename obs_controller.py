"""
OBS Controller for VibeOBS
Manages OBS WebSocket connection and scene switching operations.
"""

import logging
from typing import Dict, List, Optional, Any

try:
    from obswebsocket import obsws, requests
except ImportError:
    print("Can't import obswebsocket -- Install with: pip install obs-websocket-py")
    import sys
    sys.exit(1)


class OBSController:
    """Manages OBS WebSocket connection and scene switching"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Initialize OBS Controller
        
        Args:
            config: Configuration dictionary containing OBS settings
            logger: Logger instance for output
        """
        self.config = config
        self.logger = logger
        self.client = None
        self.available_scenes = []
        self._reconnect_attempts = 0
        self.max_reconnect_attempts = 10
    
    def connect(self) -> bool:
        """
        Connect to OBS WebSocket server
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            obs_config = self.config.get("obs", {})
            
            self.client = obsws(
                obs_config.get("host", "localhost"),
                obs_config.get("port", 4455),
                obs_config.get("password", "")
            )
            
            self.client.connect()
            self.logger.info(
                f"Connected to OBS at {obs_config.get('host')}:{obs_config.get('port')}"
            )
            
            self._reconnect_attempts = 0
            self._update_available_scenes()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to OBS: {e}")
            self.client = None
            self._reconnect_attempts += 1
            
            if self._reconnect_attempts >= self.max_reconnect_attempts:
                self.logger.error(
                    f"Max reconnection attempts ({self.max_reconnect_attempts}) reached"
                )
            
            return False
    
    def disconnect(self):
        """Disconnect from OBS WebSocket server"""
        if self.client:
            try:
                self.client.disconnect()
                self.logger.info("Disconnected from OBS")
            except Exception as e:
                self.logger.debug(f"Error during disconnect: {e}")
            finally:
                self.client = None
                self.available_scenes = []
    
    def _update_available_scenes(self):
        """Update list of available scenes from OBS"""
        if not self.client:
            return
        
        try:
            response = self.client.call(requests.GetSceneList())
            self.available_scenes = [s['sceneName'] for s in response.getScenes()]
            current_scene = response.getCurrentProgramSceneName()
            
            self.logger.debug(f"Available scenes: {self.available_scenes}")
            self.logger.debug(f"Current scene: {current_scene}")
            
        except Exception as e:
            self.logger.error(f"Error getting scene list: {e}")
            self.available_scenes = []
    
    def switch_scene(self, scene_name: str) -> bool:
        """
        Switch to specified OBS scene
        
        Args:
            scene_name: Name of the scene to switch to
            
        Returns:
            True if switch successful, False otherwise
        """
        # Connect if not connected
        if not self.client:
            if not self.connect():
                return False
        
        try:
            # Validate scene exists
            if scene_name not in self.available_scenes:
                self._update_available_scenes()  # Refresh scene list
                
                if scene_name not in self.available_scenes:
                    self.logger.warning(
                        f"Scene '{scene_name}' not found. "
                        f"Available scenes: {', '.join(self.available_scenes)}"
                    )
                    return False
            
            # Switch to the scene
            self.client.call(requests.SetCurrentProgramScene(sceneName=scene_name))
            self.logger.info(f"Switched to scene: {scene_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error switching scene: {e}")
            # Reset connection for next attempt
            self.client = None
            return False
    
    def get_current_scene(self) -> Optional[str]:
        """
        Get the name of the current scene
        
        Returns:
            Current scene name or None if not connected
        """
        if not self.client:
            return None
        
        try:
            response = self.client.call(requests.GetCurrentProgramScene())
            return response.getCurrentProgramSceneName()
        except Exception as e:
            self.logger.error(f"Error getting current scene: {e}")
            return None
    
    def get_available_scenes(self) -> List[str]:
        """
        Get list of available scenes
        
        Returns:
            List of scene names
        """
        if not self.available_scenes:
            self._update_available_scenes()
        return self.available_scenes.copy()
    
    def is_connected(self) -> bool:
        """
        Check if connected to OBS
        
        Returns:
            True if connected, False otherwise
        """
        return self.client is not None
    
    def update_config(self, new_config: Dict[str, Any]) -> bool:
        """
        Update configuration and reconnect if needed
        
        Args:
            new_config: New configuration dictionary
            
        Returns:
            True if update successful, False otherwise
        """
        old_obs = self.config.get("obs", {})
        new_obs = new_config.get("obs", {})
        
        # Check if connection settings changed
        connection_changed = (
            old_obs.get("host") != new_obs.get("host") or 
            old_obs.get("port") != new_obs.get("port") or
            old_obs.get("password") != new_obs.get("password")
        )
        
        self.config = new_config
        
        if connection_changed:
            self.logger.info("OBS connection settings changed, reconnecting...")
            self.disconnect()
            return self.connect()
        
        return True
    
    def reset_reconnect_counter(self):
        """Reset the reconnection attempts counter"""
        self._reconnect_attempts = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get OBS connection statistics
        
        Returns:
            Dictionary with connection stats
        """
        return {
            "connected": self.is_connected(),
            "reconnect_attempts": self._reconnect_attempts,
            "available_scenes": len(self.available_scenes),
            "current_scene": self.get_current_scene()
        }