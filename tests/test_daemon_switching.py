#!/usr/bin/env python3
"""
Test script to verify daemon is detecting app switches properly
"""

import time
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DaemonTest")

def test_daemon_switching():
    """Test the daemon's app switching detection"""
    
    print("=== Testing VibeOBS Daemon App Switching ===")
    print()
    print("This script will help you test if the daemon is detecting app switches.")
    print("Make sure the daemon is running in another terminal:")
    print("  source .venv/bin/activate && python vibeobs_daemon.py")
    print()
    
    input("Press Enter when the daemon is running...")
    print()
    
    # Test app switching
    apps_to_test = [
        ("Alacritty", "terminal-f"),
        ("Google Chrome", "browser-focused"),
        ("Emacs", "editor-focused"),
    ]
    
    print("Testing automatic scene switching...")
    print("Watch your OBS scenes as we switch between applications:")
    print()
    
    for i, (app_name, expected_scene) in enumerate(apps_to_test):
        print(f"{i+1}. Please switch to {app_name}")
        print(f"   Expected scene: {expected_scene}")
        print("   (Switch now and wait 3 seconds)")
        
        time.sleep(3)
        print("   ✓ Waited 3 seconds")
        print()
    
    print("Testing completed!")
    print()
    print("If scenes didn't switch automatically:")
    print("1. Check if the daemon is still running")
    print("2. Verify the app names in config.yaml match exactly")
    print("3. Check daemon logs for errors")
    print("4. Ensure OBS scenes exist with the correct names")

if __name__ == "__main__":
    test_daemon_switching()