#!/usr/bin/env python3

import time
import subprocess
from pathlib import Path

print("OBS Scene Switching Test")
print("========================")
print()
print("This will demonstrate automatic scene switching.")
print("Make sure OBS is open and the daemon is running.")
print()

apps_to_test = [
    ("Finder", "entire-screen", "Opening Finder..."),
    ("Alacritty", "terminal-f", "Switching to Terminal..."),
    ("Safari", "browser-focused", "Opening Safari...")
]

for app_name, expected_scene, message in apps_to_test:
    print(f"\n{message}")
    print(f"  App: {app_name} → Scene: {expected_scene}")
    
    # Use AppleScript to activate the application
    script = f'tell application "{app_name}" to activate'
    subprocess.run(['osascript', '-e', script], capture_output=True)
    
    print(f"  ✓ Activated {app_name}")
    print("  Waiting 3 seconds for scene switch...")
    time.sleep(3)

print("\n✅ Test complete! Check OBS to verify scenes switched correctly.")