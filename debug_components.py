#!/usr/bin/env python3
"""
Debug script to test individual components of VibeOBS
"""

import logging
import time
from config_manager import ConfigManager
from obs_controller import OBSController
from window_monitor import WindowMonitor

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VibeOBS-Debug")

def test_config_manager():
    """Test configuration loading"""
    print("\n" + "="*50)
    print("Testing ConfigManager")
    print("="*50)
    
    config_manager = ConfigManager()
    config = config_manager.load()
    
    if config:
        print("✓ Config loaded successfully")
        print(f"  Config path: {config_manager.actual_config_path}")
        print(f"  OBS host: {config.get('obs', {}).get('host')}")
        print(f"  App mappings: {list(config.get('app_scene_mappings', {}).keys())}")
        return config
    else:
        print("❌ Config loading failed")
        return None

def test_window_monitor():
    """Test window monitoring"""
    print("\n" + "="*50)
    print("Testing WindowMonitor")
    print("="*50)
    
    try:
        monitor = WindowMonitor(logger)
        print("✓ Window monitor created successfully")
        print(f"  Monitor type: {type(monitor).__name__}")
        
        # Test getting current app
        current_app = monitor.get_active_app()
        print(f"  Current app: {current_app}")
        
        # Test callback registration
        def test_callback(old_app, new_app):
            print(f"  Callback triggered: {old_app} → {new_app}")
        
        monitor.register_callback(test_callback)
        print("✓ Callback registered successfully")
        
        # Test monitoring for 10 seconds
        print("  Monitoring for app changes (10 seconds)...")
        print("  Switch between applications to test detection")
        
        start_time = time.time()
        while time.time() - start_time < 10:
            changed_app = monitor.check_and_notify()
            if changed_app:
                print(f"  App change detected: {changed_app}")
            time.sleep(0.5)
        
        stats = monitor.get_stats()
        print(f"  Final stats: {stats}")
        return monitor
        
    except Exception as e:
        print(f"❌ Window monitor failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_obs_controller(config):
    """Test OBS connection and control"""
    print("\n" + "="*50)
    print("Testing OBSController")
    print("="*50)
    
    if not config:
        print("❌ No config available for OBS test")
        return None
    
    try:
        obs = OBSController(config, logger)
        print("✓ OBS controller created successfully")
        
        # Test connection
        if obs.connect():
            print("✓ Connected to OBS successfully")
            
            # Get available scenes
            scenes = obs.get_available_scenes()
            print(f"  Available scenes: {scenes}")
            
            # Get current scene
            current_scene = obs.get_current_scene()
            print(f"  Current scene: {current_scene}")
            
            # Test scene switching (if scenes exist)
            if scenes and len(scenes) > 1:
                test_scene = scenes[1] if current_scene != scenes[1] else scenes[0]
                print(f"  Testing scene switch to: {test_scene}")
                if obs.switch_scene(test_scene):
                    print("✓ Scene switch successful")
                else:
                    print("❌ Scene switch failed")
            
            stats = obs.get_stats()
            print(f"  OBS stats: {stats}")
            
            obs.disconnect()
            return obs
        else:
            print("❌ Failed to connect to OBS")
            return None
            
    except Exception as e:
        print(f"❌ OBS controller failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_integration(config):
    """Test full integration"""
    print("\n" + "="*50)
    print("Testing Integration")
    print("="*50)
    
    if not config:
        print("❌ No config available for integration test")
        return
    
    try:
        # Create components
        monitor = WindowMonitor(logger)
        obs = OBSController(config, logger)
        
        # Connect to OBS
        if not obs.connect():
            print("❌ Failed to connect to OBS for integration test")
            return
        
        # Define integration callback
        def integration_callback(old_app, new_app):
            print(f"Integration: App changed {old_app} → {new_app}")
            
            mappings = config.get('app_scene_mappings', {})
            if new_app in mappings:
                scene_name = mappings[new_app]
                print(f"  Switching to scene: {scene_name}")
                success = obs.switch_scene(scene_name)
                print(f"  Scene switch {'successful' if success else 'failed'}")
            else:
                print(f"  No mapping found for app: {new_app}")
        
        # Register callback
        monitor.register_callback(integration_callback)
        print("✓ Integration callback registered")
        
        # Monitor for 15 seconds
        print("  Monitoring integration for 15 seconds...")
        print("  Switch between mapped applications to test automatic scene switching")
        
        start_time = time.time()
        while time.time() - start_time < 15:
            monitor.check_and_notify()
            time.sleep(0.5)
        
        obs.disconnect()
        print("✓ Integration test completed")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all debug tests"""
    print("VibeOBS Component Debug Tool")
    print("=" * 50)
    
    # Test each component
    config = test_config_manager()
    monitor = test_window_monitor()
    obs = test_obs_controller(config)
    
    # Test integration if all components work
    if config and monitor and obs:
        test_integration(config)
    else:
        print("\n❌ Skipping integration test due to component failures")
    
    print("\nDebug testing completed!")

if __name__ == "__main__":
    main()