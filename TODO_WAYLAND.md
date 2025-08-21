# Wayland Support Implementation TODO

## Current Status
- ✅ Basic Linux support with X11 tools (xdotool, wmctrl, xprop)
- ✅ Fallback process-based detection
- ❌ Limited Wayland support (falls back to process detection)

## Wayland Challenges
- No universal "active window" concept like X11
- Compositor-specific implementations required
- Security model prevents cross-client window access
- GNOME refuses `wlr-foreign-toplevel-management` protocol for security

## Implementation Plan

### 1. Desktop Environment Detection
```python
def detect_desktop_environment():
    """Detect current desktop environment and compositor"""
    # Check environment variables and running processes
    # XDG_CURRENT_DESKTOP, XDG_SESSION_DESKTOP
    # Running processes: gnome-shell, kwin, sway, hyprland
```

### 2. Compositor-Specific Implementations

#### **Sway/i3 Support** (High Priority)
```python
def _get_active_app_sway(self) -> Optional[str]:
    """Get active app using swaymsg"""
    # swaymsg -t get_tree | jq '.. | (.nodes? // empty)[] | select(.focused==true)'
    # Parse JSON tree to find focused window
```

#### **Hyprland Support** (High Priority) 
```python
def _get_active_app_hyprland(self) -> Optional[str]:
    """Get active app using hyprctl"""
    # hyprctl activewindow -j | jq --raw-output .class
    # Alternative: Monitor IPC socket for real-time updates
```

#### **GNOME Support** (Medium Priority)
```python
def _get_active_app_gnome_dbus(self) -> Optional[str]:
    """Get active app via GNOME Shell D-Bus"""
    # Use gdbus to query org.gnome.Shell
    # May require GNOME Shell extension for window focus info
    # Alternative: org.gnome.Mutter.DisplayConfig
```

#### **KDE Plasma Support** (Medium Priority)
```python
def _get_active_app_kde_dbus(self) -> Optional[str]:
    """Get active app via KDE D-Bus"""
    # Use qdbus to query org.kde.KWin
    # KWin exposes window management via D-Bus
```

### 3. Protocol-Based Solutions

#### **wlr-foreign-toplevel-management** (wlroots compositors)
```python
def _get_active_app_wlr_protocol(self) -> Optional[str]:
    """Use wlr-foreign-toplevel-management protocol"""
    # Available in: Sway, Mir, Phosh, Wayfire
    # NOT available in: GNOME, KDE
    # Requires python-wayland bindings
```

#### **ext-foreign-toplevel-list** (Newer protocol)
```python
def _get_active_app_ext_toplevel(self) -> Optional[str]:
    """Use ext-foreign-toplevel-list protocol"""
    # Newer protocol, limited compositor support
```

### 4. Enhanced Process Detection
```python
def _get_active_app_enhanced_process(self) -> Optional[str]:
    """Enhanced process-based detection for Wayland"""
    # Monitor /proc/*/stat for recent CPU activity
    # Check systemd-logind session information
    # Look for processes with recent input events
    # Cross-reference with known GUI process patterns
```

### 5. Integration with Status Bars
```python
def _get_active_app_waybar(self) -> Optional[str]:
    """Get window info from Waybar/other status bars"""
    # Some status bars expose window information
    # Can be used as a data source
```

## Dependencies to Add

### Core Wayland Libraries
```python
# requirements-wayland.txt
python-wayland>=0.4.0  # Wayland protocol bindings
pydbus>=0.6.0         # D-Bus communication (GNOME/KDE)
```

### System Tools Detection
```bash
# Tools to detect and use
swaymsg      # Sway compositor
hyprctl      # Hyprland compositor  
gdbus        # GNOME D-Bus queries
qdbus        # KDE D-Bus queries
wlr-randr    # wlroots-based compositors
```

## Implementation Strategy

### Phase 1: Compositor Detection
- [ ] Add desktop environment detection
- [ ] Update `_detect_available_methods()` with Wayland tools
- [ ] Add session type detection (X11 vs Wayland)

### Phase 2: High-Priority Compositors
- [ ] Implement Sway support (`swaymsg`)
- [ ] Implement Hyprland support (`hyprctl`)
- [ ] Test on popular distributions

### Phase 3: Desktop Environment Support
- [ ] Implement GNOME D-Bus support
- [ ] Implement KDE D-Bus support
- [ ] Add fallback mechanisms

### Phase 4: Protocol Support
- [ ] Add python-wayland dependency
- [ ] Implement wlr-foreign-toplevel-management
- [ ] Implement ext-foreign-toplevel-list

### Phase 5: Enhanced Fallbacks
- [ ] Improve process-based detection
- [ ] Add activity monitoring
- [ ] Integration with status bar data

## Testing Plan

### Test Environments
- [ ] **Sway** (Arch, Fedora)
- [ ] **Hyprland** (Arch)
- [ ] **GNOME** (Ubuntu, Fedora)
- [ ] **KDE Plasma** (Kubuntu, openSUSE)
- [ ] **Other wlroots** (Wayfire, River)

### Test Scenarios
- [ ] Fresh Wayland session
- [ ] Mixed X11/Wayland applications
- [ ] Rapid window switching
- [ ] Multi-monitor setups
- [ ] Compositor restart/reload

## Configuration Updates

### Wayland-Specific Config
```yaml
wayland:
  preferred_method: auto  # auto, sway, hyprland, gnome, kde
  fallback_enabled: true
  enhanced_process_detection: true
  polling_interval_wayland: 0.3  # Faster polling for Wayland
```

## Known Limitations

### GNOME Limitations
- No `wlr-foreign-toplevel-management` support
- Requires D-Bus queries or shell extensions
- May need user permissions for window access

### Security Considerations
- Some methods require additional permissions
- Wayland's security model limits cross-process access
- May need user consent for window information

### Performance Considerations  
- D-Bus queries may have higher latency
- JSON parsing overhead for `swaymsg`/`hyprctl`
- Protocol-based solutions more efficient

## Future Enhancements

### Real-time Monitoring
- [ ] IPC socket monitoring (Hyprland, Sway)
- [ ] D-Bus signal subscriptions
- [ ] Event-driven updates vs polling

### Window Metadata
- [ ] Window titles for better scene mapping
- [ ] Application instance detection
- [ ] Workspace/virtual desktop awareness

### Integration Improvements
- [ ] Better error handling and fallbacks
- [ ] Automatic compositor detection
- [ ] Performance optimization for different methods

## References
- [Sway IPC Documentation](https://github.com/swaywm/sway/blob/master/sway/sway-ipc.7.scd)
- [Hyprland IPC Documentation](https://wiki.hypr.land/IPC/)
- [wlr-protocols](https://gitlab.freedesktop.org/wlroots/wlr-protocols)
- [Wayland Protocol Documentation](https://wayland.freedesktop.org/docs/html/)
- [ActivityWatch Wayland Implementation](https://github.com/ActivityWatch/aw-watcher-window-wayland)

---

**Priority:** Medium (after core stability)
**Complexity:** High (compositor-specific implementations)
**Impact:** High (enables full Linux support)