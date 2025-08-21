"""
Window Monitor for VibeOBS
Monitors active window/application changes on macOS.
"""

import logging
from typing import Optional, Callable, Dict, Any

try:
    from AppKit import NSWorkspace
except ImportError:
    print("Can't import AppKit -- Install with: pip install PyObjC")
    import sys
    sys.exit(1)


class WindowMonitor:
    """Monitors active window/application on macOS"""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize Window Monitor
        
        Args:
            logger: Logger instance for output
        """
        self.logger = logger
        self.last_active_app = None
        self.app_change_callbacks = []
        self._app_history = []
        self._max_history = 10
    
    def get_active_app(self) -> Optional[str]:
        """
        Get name of currently active application
        
        Returns:
            Application name or None if error
        """
        try:
            workspace = NSWorkspace.sharedWorkspace()
            active_app = workspace.activeApplication()
            return active_app['NSApplicationName']
            
        except Exception as e:
            self.logger.error(f"Error getting active application: {e}")
            return None
    
    def get_active_app_info(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about the active application
        
        Returns:
            Dictionary with app info or None if error
        """
        try:
            workspace = NSWorkspace.sharedWorkspace()
            active_app = workspace.activeApplication()
            
            return {
                'name': active_app.get('NSApplicationName'),
                'bundle_id': active_app.get('NSApplicationBundleIdentifier'),
                'path': active_app.get('NSApplicationPath'),
                'process_id': active_app.get('NSApplicationProcessIdentifier')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting active application info: {e}")
            return None
    
    def has_app_changed(self, current_app: str) -> bool:
        """
        Check if active app has changed
        
        Args:
            current_app: Name of the current active app
            
        Returns:
            True if app has changed, False otherwise
        """
        if current_app and current_app != self.last_active_app:
            # Add to history
            if self.last_active_app:
                self._add_to_history(self.last_active_app)
            
            self.last_active_app = current_app
            return True
        return False
    
    def _add_to_history(self, app_name: str):
        """
        Add app to history
        
        Args:
            app_name: Name of the application
        """
        self._app_history.append(app_name)
        if len(self._app_history) > self._max_history:
            self._app_history.pop(0)
    
    def get_app_history(self) -> list:
        """
        Get application switch history
        
        Returns:
            List of previously active applications
        """
        return self._app_history.copy()
    
    def get_last_app(self) -> Optional[str]:
        """
        Get the previously active application
        
        Returns:
            Previous app name or None
        """
        if self._app_history:
            return self._app_history[-1]
        return None
    
    def register_callback(self, callback: Callable[[str, str], None]):
        """
        Register a callback for app changes
        
        Args:
            callback: Function to call on app change (old_app, new_app)
        """
        if callback not in self.app_change_callbacks:
            self.app_change_callbacks.append(callback)
            self.logger.debug(f"Registered callback: {callback.__name__}")
    
    def unregister_callback(self, callback: Callable[[str, str], None]):
        """
        Unregister a callback
        
        Args:
            callback: Callback function to remove
        """
        if callback in self.app_change_callbacks:
            self.app_change_callbacks.remove(callback)
            self.logger.debug(f"Unregistered callback: {callback.__name__}")
    
    def check_and_notify(self) -> Optional[str]:
        """
        Check for app changes and notify callbacks
        
        Returns:
            Current app name if changed, None otherwise
        """
        current_app = self.get_active_app()
        
        if current_app and self.has_app_changed(current_app):
            # Notify all callbacks
            for callback in self.app_change_callbacks:
                try:
                    callback(self.get_last_app(), current_app)
                except Exception as e:
                    self.logger.error(f"Error in callback {callback.__name__}: {e}")
            
            return current_app
        
        return None
    
    def reset(self):
        """Reset monitor state"""
        self.last_active_app = None
        self._app_history.clear()
        self.logger.debug("Window monitor reset")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get monitor statistics
        
        Returns:
            Dictionary with monitor stats
        """
        return {
            "current_app": self.last_active_app,
            "previous_app": self.get_last_app(),
            "history_count": len(self._app_history),
            "callbacks_registered": len(self.app_change_callbacks)
        }