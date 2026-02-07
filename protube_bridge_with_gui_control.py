import ctypes
import socket
import time
import threading
import json
import os
from datetime import datetime

print("Starting ProTube Bridge with 3-Mode Fire Selector...")

# Load the ForceTube DLL
print("Loading ForceTube DLL...")
forcetube = ctypes.CDLL("./ForceTubeVR_API_x64.dll")
print("DLL loaded!")

# Define function signatures for battery access (if available)
try:
    # Try to access battery function - signature may vary
    forcetube.GetBatteryLevel.argtypes = [ctypes.c_int]
    forcetube.GetBatteryLevel.restype = ctypes.c_int
    battery_available = True
    print("Battery monitoring available")
except:
    battery_available = False
    print("Battery monitoring not available in this API version")

# Initialize ProVolver
print("Initializing ProVolver...")
forcetube.InitAsync()
time.sleep(3)
print("ProVolver initialized!")

# === CONFIGURATION ===
UDP_IP = "127.0.0.1"
UDP_PORT = 5015  # Receive from C++ driver only

CONFIG_FILE = "protube_gui_config.json"
BATTERY_FILE = "protube_battery.txt"

# Driver config file - must match path in C++ DLL
DOCUMENTS_PATH = os.path.join(os.path.expanduser("~"), "Documents", "ProTube OpenXR Companion")
DRIVER_CONFIG_FILE = os.path.join(DOCUMENTS_PATH, "protube_config.txt")

# Fire mode constants
SINGLE_SHOT = 0
BURST_FIRE = 1
FULL_AUTO = 2
HAPTIC_EXPERIMENTAL = 3

MODE_NAMES = {
    SINGLE_SHOT: "SINGLE SHOT",
    BURST_FIRE: "BURST FIRE",
    FULL_AUTO: "FULL AUTO",
    HAPTIC_EXPERIMENTAL: "HAPTIC EXPERIMENTAL"
}

# Default settings
config = {
    "mode_select": "Haptic Filtered",
    "feedback": True,
    "ignore_left_hand": False,
    "ignore_right_hand": False,
    "latency": 0,
    "filter_window_ms": 60,
    "single_kick": 100,
    "single_rumble": 47,
    "single_duration": 100,
    "burst_kick": 100,
    "burst_rumble": 47,
    "burst_duration": 100,
    "burst_count": 3,
    "auto_kick": 100,
    "auto_rumble": 47,
    "auto_duration": 100,
    "auto_rate": 60
}

# Config lock for thread safety
config_lock = threading.Lock()
last_config_mtime = 0

# === STATE TRACKING ===
current_mode = SINGLE_SHOT
trigger_held = {'right': False, 'left': False}

# Auto-fire threading
auto_fire_active = {'right': False, 'left': False}
auto_fire_threads = {'right': None, 'left': None}
stop_auto_fire = {'right': threading.Event(), 'left': threading.Event()}

# Burst fire cooldown tracking
last_burst_time = {'right': None, 'left': None}

# Bridge status
bridge_running = True


def percent_to_raw(percent):
    """Convert percentage (0-100) to raw value (0-255)"""
    return int(percent * 2.55)


def load_config():
    """Load configuration from JSON file"""
    global last_config_mtime
    
    if not os.path.exists(CONFIG_FILE):
        print(f"[CONFIG] No config file found, using defaults")
        return
    
    try:
        # Check if file has been modified
        mtime = os.path.getmtime(CONFIG_FILE)
        if mtime == last_config_mtime:
            return  # No changes
        
        with open(CONFIG_FILE, 'r') as f:
            new_config = json.load(f)
        
        with config_lock:
            config.update(new_config)
        
        last_config_mtime = mtime
        
        # Write driver config file for C++ driver
        write_driver_config()
        
        print(f"\n{'='*50}")
        print(f"CONFIG LOADED")
        print(f"{'='*50}")
        print(f"  Mode: {config['mode_select']}")
        print(f"  Feedback: {config['feedback']}")
        print(f"  Latency: {config['latency']}ms")
        print(f"  Single: Kick={config['single_kick']}% Rumble={config['single_rumble']}% Dur={config['single_duration']}ms")
        print(f"  Burst: Kick={config['burst_kick']}% Rumble={config['burst_rumble']}% Dur={config['burst_duration']}ms Count={config['burst_count']}")
        print(f"  Auto: Kick={config['auto_kick']}% Rumble={config['auto_rumble']}% Dur={config['auto_duration']}ms Rate={config['auto_rate']}ms")
        print(f"{'='*50}\n")
        
    except Exception as e:
        print(f"[CONFIG] Error loading config: {e}")


def write_driver_config():
    """Write config file for C++ driver to read"""
    try:
        with config_lock:
            mode_select = config['mode_select']
            filter_window = config.get('filter_window_ms', 60)
        
        # Map GUI mode names to driver mode names
        mode_map = {
            "Trigger": "trigger",
            "Haptic Filtered": "haptic_filtered",
            "Haptic Experimental A": "haptic_experimental_a",  # Filtered mode, disables B button
            "Haptic Experimental B": "haptic_experimental_b"   # Unfiltered mode, disables B button
        }
        
        driver_mode = mode_map.get(mode_select, "haptic_filtered")
        
        # Ensure directory exists
        os.makedirs(DOCUMENTS_PATH, exist_ok=True)
        
        # Write simple text config for C++ driver
        with open(DRIVER_CONFIG_FILE, 'w') as f:
            f.write(f"mode={driver_mode}\n")
            f.write(f"kick_strength=255\n")
            f.write(f"kick_duration=100\n")
            f.write(f"filter_window_ms={filter_window}\n")
        
        print(f"[DRIVER CONFIG] Written: mode={driver_mode}, filter={filter_window}ms")
        print(f"[DRIVER CONFIG] Location: {DRIVER_CONFIG_FILE}")
        
    except Exception as e:
        print(f"[DRIVER CONFIG] Error writing: {e}")


def config_watcher():
    """Watch config file for changes and reload"""
    global bridge_running
    
    print("[CONFIG] Config file watcher started")
    
    while bridge_running:
        load_config()
        time.sleep(1.0)  # Check every second
    
    print("[CONFIG] Config file watcher stopped")


def battery_watcher():
    """Monitor battery level and write to file for GUI"""
    global bridge_running
    
    if not battery_available:
        return
    
    print("[BATTERY] Battery monitor started")
    
    while bridge_running:
        try:
            # Try to get battery level for right hand (channel 4)
            # Function signature may vary - trying common patterns
            battery_level = forcetube.GetBatteryLevel(4)
            
            # Write to file for GUI to read
            with open(BATTERY_FILE, 'w') as f:
                f.write(str(battery_level))
            
            # Only print on battery level changes
            if not hasattr(battery_watcher, 'last_level') or battery_watcher.last_level != battery_level:
                print(f"[BATTERY] Level: {battery_level}%")
                battery_watcher.last_level = battery_level
                
        except Exception as e:
            # If battery function doesn't work, write a default value
            with open(BATTERY_FILE, 'w') as f:
                f.write("100")  # Default to 100% if we can't read it
        
        time.sleep(10.0)  # Check every 10 seconds
    
    print("[BATTERY] Battery monitor stopped")


def get_mode_config(mode):
    """Get kick/rumble/duration for a specific mode"""
    with config_lock:
        if mode == SINGLE_SHOT:
            kick = percent_to_raw(config["single_kick"])
            rumble = percent_to_raw(config["single_rumble"])
            duration = config["single_duration"]
        elif mode == BURST_FIRE:
            kick = percent_to_raw(config["burst_kick"])
            rumble = percent_to_raw(config["burst_rumble"])
            duration = config["burst_duration"]
        elif mode == FULL_AUTO:
            kick = percent_to_raw(config["auto_kick"])
            rumble = percent_to_raw(config["auto_rumble"])
            duration = config["auto_duration"]
        else:
            kick, rumble, duration = 255, 120, 100
    
    return kick, rumble, duration


def send_kick_feedback(channel, num_pulses):
    """Send weak kick feedback pattern (1-3 pulses = mode indicator)"""
    with config_lock:
        if not config["feedback"]:
            print(f"  [KICK FEEDBACK] Disabled in settings")
            return
    
    print(f"  [KICK FEEDBACK] Sending {num_pulses} light kicks to channel {channel}")
    for i in range(num_pulses):
        print(f"    Kick {i+1}: Shot(1, 0, 5, {channel})")
        forcetube.Shot(1, 0, 5, channel)  # Minimal kick=1, no rumble, duration=5ms
        if i < num_pulses - 1:
            time.sleep(0.175)  # 175ms between kicks


def handle_mode_change(mode_name):
    """Switch fire mode and provide kick feedback"""
    global current_mode
    
    if mode_name == "single":
        current_mode = SINGLE_SHOT
        pulses = 1
    elif mode_name == "burst":
        current_mode = BURST_FIRE
        pulses = 2
    elif mode_name == "auto":
        current_mode = FULL_AUTO
        pulses = 3
    else:
        return
    
    print(f"\n{'='*50}")
    print(f"MODE CHANGED: {MODE_NAMES[current_mode]}")
    print(f"{'='*50}\n")
    
    # Send light kick feedback on right hand (where mode button is)
    send_kick_feedback(4, pulses)


def auto_fire_loop(hand, channel):
    """Continuously kick while trigger is held in full auto mode"""
    print(f"  [AUTO-FIRE START] {hand.upper()} hand")
    
    while not stop_auto_fire[hand].is_set() and trigger_held[hand]:
        kick, rumble, duration = get_mode_config(FULL_AUTO)
        with config_lock:
            fire_rate = config["auto_rate"]
        
        forcetube.Shot(kick, rumble, duration, channel)
        time.sleep(fire_rate / 1000.0)
    
    auto_fire_active[hand] = False
    print(f"  [AUTO-FIRE STOP] {hand.upper()} hand")


def handle_shot(hand, channel):
    """Handle shot based on current fire mode"""
    
    # Apply latency if configured
    with config_lock:
        latency_ms = config["latency"]
    
    if latency_ms > 0:
        time.sleep(latency_ms / 1000.0)
    
    if current_mode == SINGLE_SHOT:
        kick, rumble, duration = get_mode_config(SINGLE_SHOT)
        forcetube.Shot(kick, rumble, duration, channel)
        print(f"  [SINGLE] {hand}")
        
    elif current_mode == BURST_FIRE:
        # Check cooldown
        now = datetime.now()
        
        with config_lock:
            burst_cooldown = 200  # Fixed cooldown
        
        if last_burst_time[hand] is not None:
            time_since_last_burst = (now - last_burst_time[hand]).total_seconds() * 1000
            if time_since_last_burst < burst_cooldown:
                print(f"  [BURST COOLDOWN] {hand} - too soon, ignoring")
                return
        
        # Get burst settings
        kick, rumble, duration = get_mode_config(BURST_FIRE)
        with config_lock:
            burst_count = config["burst_count"]
            burst_rate = config["auto_rate"]  # Use auto_rate for burst spacing
        
        # Burst: Multiple rapid kicks
        for i in range(burst_count):
            forcetube.Shot(kick, rumble, duration, channel)
            if i < burst_count - 1:
                time.sleep(burst_rate / 1000.0)
        
        last_burst_time[hand] = now
        print(f"  [BURST] {burst_count} rounds ({hand})")
        
    elif current_mode == FULL_AUTO:
        # Full auto: Start continuous fire if trigger is held
        if trigger_held[hand] and not auto_fire_active[hand]:
            auto_fire_active[hand] = True
            stop_auto_fire[hand].clear()
            
            auto_fire_threads[hand] = threading.Thread(
                target=auto_fire_loop,
                args=(hand, channel),
                daemon=True
            )
            auto_fire_threads[hand].start()
    
    elif current_mode == HAPTIC_EXPERIMENTAL:
        # Haptic Experimental: Immediate passthrough with no fire mode logic
        # Uses Single Shot settings for customization
        kick, rumble, duration = get_mode_config(SINGLE_SHOT)
        forcetube.Shot(kick, rumble, duration, channel)
        print(f"  [EXPERIMENTAL] {hand}")


def handle_trigger_state(hand, state):
    """Handle trigger press/release for full auto mode"""
    was_held = trigger_held[hand]
    trigger_held[hand] = (state == "1")
    
    # Trigger state changed
    if was_held and not trigger_held[hand]:
        # Trigger released - stop auto fire
        if auto_fire_active[hand]:
            stop_auto_fire[hand].set()
    elif not was_held and trigger_held[hand]:
        # Trigger pressed - will be handled by shot message
        pass


# Load initial config
load_config()

# Start config file watcher in separate thread
config_thread = threading.Thread(target=config_watcher, daemon=True)
config_thread.start()

# Start battery monitor in separate thread
battery_thread = threading.Thread(target=battery_watcher, daemon=True)
battery_thread.start()

# Set up UDP listener for driver messages
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.5)  # 500ms timeout for responsive shutdown

print(f"\nListening on port {UDP_PORT} (driver messages)...")
print(f"Watching config file: {CONFIG_FILE}")
print(f"\nFire Mode Controls:")
print(f"  B Button (upper right button on right controller):")
print(f"    Hold 1 second   = Single Shot")
print(f"    Double tap      = Burst Fire")
print(f"    Triple tap      = Full Auto")
print(f"\nCurrent Mode: {MODE_NAMES[current_mode]}")
print(f"\nKick Feedback:")
print(f"  1 pulse  = Single Shot")
print(f"  2 pulses = Burst Fire")
print(f"  3 pulses = Full Auto")
print(f"\nWaiting for input...\n")

try:
    while bridge_running:
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode('utf-8').strip()
            
            # Mode changes
            if message.startswith("mode:"):
                mode_name = message.split(":")[1]
                handle_mode_change(mode_name)
            
            # Trigger state updates (for full auto)
            elif message.startswith("trigger_"):
                parts = message.split(":")
                # Swap right/left to match actual controller orientation
                hand = "left" if "right" in parts[0] else "right"
                state = parts[1]
                
                # Check if hand should be ignored
                if hand == "left":
                    with config_lock:
                        ignore_left = config.get("ignore_left_hand", False)
                    if ignore_left:
                        continue  # Skip left hand trigger events
                elif hand == "right":
                    with config_lock:
                        ignore_right = config.get("ignore_right_hand", False)
                    if ignore_right:
                        continue  # Skip right hand trigger events
                
                handle_trigger_state(hand, state)
            
            # Shot events (from haptics)
            elif message == "shot_right":
                # Check if left hand should be ignored (right message = left controller)
                with config_lock:
                    ignore_left = config.get("ignore_left_hand", False)
                if not ignore_left:
                    handle_shot('left', 5)
            elif message == "shot_left":
                # Check if right hand should be ignored (left message = right controller)
                with config_lock:
                    ignore_right = config.get("ignore_right_hand", False)
                if not ignore_right:
                    handle_shot('right', 4)
            
            # Debug messages
            elif message.startswith("duration:"):
                pass  # Ignore debug duration messages
            else:
                print(f"Received: {message}")
        
        except socket.timeout:
            continue  # Normal timeout, keep looping
        except Exception as e:
            if bridge_running:
                print(f"Error processing message: {e}")
            
except KeyboardInterrupt:
    print("\nShutting down...")
finally:
    bridge_running = False
    
    # Stop all auto-fire threads
    for hand in ['right', 'left']:
        if auto_fire_active[hand]:
            stop_auto_fire[hand].set()
    
    # Wait for watcher threads to finish
    config_thread.join(timeout=2.0)
    if battery_available:
        battery_thread.join(timeout=2.0)
    
    # Clean up battery file
    if os.path.exists(BATTERY_FILE):
        try:
            os.remove(BATTERY_FILE)
        except:
            pass
    
    # Clean up driver config file
    if os.path.exists(DRIVER_CONFIG_FILE):
        try:
            os.remove(DRIVER_CONFIG_FILE)
        except:
            pass
    
    sock.close()
    print("Bridge closed.")
