#!/usr/bin/env python3

import json
from pathlib import Path
from obswebsocket import obsws, requests

# Load config
config_path = Path("config.json")
with open(config_path, 'r') as f:
    config = json.load(f)

obs_config = config["obs"]
print(f"Testing OBS connection:")
print(f"  Host: {obs_config['host']}")
print(f"  Port: {obs_config['port']}")
print(f"  Password: {'*' * len(obs_config['password'])} ({len(obs_config['password'])} chars)")
print()

try:
    # Try to connect
    print("Attempting connection...")
    client = obsws(
        obs_config["host"],
        obs_config["port"],
        obs_config["password"]
    )
    client.connect()
    print("✓ Connected successfully!")
    
    # Get version info
    version = client.call(requests.GetVersion())
    print(f"✓ OBS Version: {version.getObsVersion()}")
    print(f"✓ WebSocket Version: {version.getObsWebSocketVersion()}")
    
    # Get scenes
    scenes = client.call(requests.GetSceneList())
    scene_names = [s['sceneName'] for s in scenes.getScenes()]
    print(f"✓ Available scenes: {scene_names}")
    print(f"✓ Current scene: {scenes.getCurrentProgramSceneName()}")
    
    client.disconnect()
    print("\n✅ Connection test successful!")
    
except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    print("\nPossible issues:")
    print("1. Check if OBS is running")
    print("2. Verify WebSocket Server is enabled in OBS (Tools → WebSocket Server Settings)")
    print("3. Confirm the password matches exactly")
    print("4. Check if the host/port are correct")