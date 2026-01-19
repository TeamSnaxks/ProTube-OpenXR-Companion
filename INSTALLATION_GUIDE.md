# ProTube OpenXR Companion - Installation Guide

## About 

The ProTube Companion app that comes with your haptic module is a great addition for non-native games, however it uses SteamVR by default. If using UEVR, this is an un-needed step that costs major performance since you need to run SteamVR within Virtual Desktop, to use your ProTube device. 

This app allows use of OpenXR/VDXR to eliminate SteamVR altogether. Additionally, when playing non-ProTube supported VR titles, you can use OpenComposite to switch the runtime to OpenXR and then use this app as well. 

OpenXR is more efficient and allows for other tools such as OpenXR Toolkit, to improve performance further. Overall this app is intended for people that want to squeeze out the most performance possible, and make using ProTube gear easier. 

Additionally it has features that the original ProTube Companion app does not, such as creating custom loadouts split by class (single shot, burst, full auto). It also communicates ammo-out in the Haptic modes (*unless you hold the trigger down indefinitely in full auto mode). Last, it eliminates the annoying "kick on trigger release" behavior of SteamVR.

The Trigger mode also behaves like a software version of the ProVolver Elite, but with more customization. 


## Disclaimer

This is an unofficial modification. Not affiliated with or endorsed by ProTubeVR or Virtual Desktop. All testing was done with a ProVolver (Original) unit.
Use at your own risk. Always backup original files before installation. 

Improper use of the haptic filter, shot duration and latency compensation options at their extremes can create unwanted repeat cycling of the device. Please understand what each does and how it relates to your game's haptics before setting. The red "STOP BRIDGE" doubles as a kill switch if needed.  

---

**Version:** 1.01  
**Last Updated:** January 2026



## Simple 3-Step Installation

No installer needed - just follow these simple steps!

---

## Prerequisites

Before installing, ensure you have:

1. **Virtual Desktop / Virtual Desktop Streamer** 
2. **ProTube VR Hardware** 

---

## Installation Steps

### Step 1: Backup & Replace Virtual Desktop DLL

1. **Navigate to Virtual Desktop Streamer folder:**
   - Open File Explorer
   - Go to: `C:\Program Files\Virtual Desktop Streamer\OpenXR\`
   
2. **Backup the original DLL:**
   - Find: `virtualdesktop-openxr.dll`
   - Right-click → Rename
   - Change name to: `virtualdesktop-openxr.dll.backup`
   - **IMPORTANT:** Keep this backup! You can restore it anytime.

3. **Install the modified DLL:**
   - Open the `DLL` folder from this package
   - Copy: `virtualdesktop-openxr.dll`
   - Paste it into: `C:\Program Files\Virtual Desktop Streamer\OpenXR\`
   - **You may need administrator privileges** - click "Yes" if prompted

### Step 2: Install ProTube OpenXR Companion

1. **Copy the Companion folder:**
   - Find the `ProTube OpenXR Companion` folder in this package
   - Copy the entire folder

2. **Paste to your Documents folder:**
   - Open File Explorer
   - Navigate to: `C:\Users\[YOUR_USERNAME]\Documents\`
   - Paste the folder here
   - Final location should be: `C:\Users\[YOUR_USERNAME]\Documents\ProTube OpenXR Companion\`

### Step 3: Create Desktop Shortcut (Optional but Recommended)

1. **Navigate to the Companion folder:**
   - Go to: `C:\Users\[YOUR_USERNAME]\Documents\ProTube OpenXR Companion\`

2. **Create shortcut:**
   - Right-click on: `ProTube OpenXR Companion.exe`
   - Select: "Send to" → "Desktop (create shortcut)"
   - Optionally rename the shortcut to just: `ProTube OpenXR Companion`

**Installation Complete!** ✅

---

## First Time Setup

### Launch the Application

1. **Open the GUI:**
   - Double-click the desktop shortcut
   - OR navigate to `Documents\ProTube OpenXR Companion\` and double-click `ProTube OpenXR Companion.exe`

2. **Select the correct Haptic Mode:**
   Choose the mode that best fits your game (see Mode Selection Guide PDF for flowchart):
   
   - **Trigger Mode:** For games with no haptic support or if you want a simplified experience
   - **Haptic Filtered:** For standard shooters with haptic support (blocks damage hits)
   - **Haptic Experimental A:** For games with complex haptics - uses filtering to block damage
   - **Haptic Experimental B:** For max responsiveness - forwards all game haptics without filtering
   
   **Note:** Modes can now be switched in real-time! No need to restart your game or the Bridge.

3. **Start the Bridge:**
   - Click the **"Start Bridge"** button in the GUI
   - The Bridge Status indicator should turn green and the light will turn solid on your device
   - Battery level should display after a few moments (if supported by your ProTube model)

### Configure Your Settings

The default settings load on first launch, but you can customize and save using the Save As and Load options:

1. **Adjust Haptic Feedback:**
   - **Single Shot:** Kick strength, rumble, duration
   - **Burst Fire:** Kick strength, rumble, duration, burst count
   - **Full Auto:** Kick strength, rumble, duration, fire rate

2. **Filter Intensity (Haptic Filtered & Experimental A only):**
   - Adjustable from 30-150ms
   - Lower = tighter filtering (fewer haptics pass through)
   - Higher = more lenient (more haptics pass through)
   - Recommended: 40-80ms for most games

3. **Latency Compensation:**
   - Standard modes: 0-100ms
   - Experimental A & B: 0-10ms (these modes work best with low latency)

4. **Additional Options:**
   - **Fire Mode Feedback:** Enable/disable mode switching confirmation kicks
   - **Ignore Left Hand:** Block all left controller trigger/haptic events
   - **Ignore Right Hand:** Block all right controller trigger/haptic events

*Ignore Hand Modes can have unexpected benefits depending on how the developer implemented haptics. For example Insurgency Sandstorm (in UEVR) with Ignore Left Hand, will allow use of the Experimental B mode, and you get full haptics, uninterrupted by damage hits


5. **All settings auto-save** to "protube_gui_config.json". This file allows live changes, leave it in place and unmodified. Save your custom Configs in the "OpenXR Companion Configs" folder

---

## Understanding Haptic Modes

### Trigger Mode
- **How it works:** Generates haptic from your trigger pull (no game haptics needed)
- **Best for:** Games without haptic support, or simplified consistent feel
- **Settings:** Full customization of kick strength, rumble, and duration

### Haptic Filtered
- **How it works:** Uses game haptics but filters them based on trigger timing. You select the mode based on the weapon (Single, Burst, Full Auto)
- **Best for:** Standard shooters with basic haptic support i.e. one trigger pull = one kick regardless of weapon
- **Settings:** Adjust Filter Intensity (40-80ms recommended)
- **Blocks:** Damage hits and non-shooting haptics
- **Ammo runs out correctly

### Haptic Experimental A (Filtered Universal)
- **How it works:** Advanced filtering with universal weapon detection
- **Best for:** Games with complex haptics
- **Settings:** Adjust Filter Intensity (40-80ms recommended), Latency 0-10ms
- **Features:** Auto-detects fire rate, blocks damage, locked to Single Shot mode
- **Note:** B button is disabled (no need to manually switch fire modes like in Trigger or Haptic Filtered)
- **Ammo runs out correctly

### Haptic Experimental B (Unfiltered Universal)
- **How it works:** Forwards all game haptics directly without filtering
- **Best for:** Maximum responsiveness, games where damage filtering isn't needed
- **Settings:** Latency 0-10ms (no filter control)
- **Features:** Auto-detects fire rate, all haptics pass through, locked to Single Shot mode
- **Note:** B button is disabled (cannot manually switch fire modes)
- **Ammo runs out correctly


---

## Usage

### In-Game Fire Mode Controls

Use the **B Button** (upper right button on right controller):
- **Hold 1 second** = Single Shot Mode
- **Double tap** = Burst Fire Mode  
- **Triple tap** = Full Auto Mode

**Mode Confirmation:**
You'll feel low strength kicks confirming the mode:
- 1 pulse = Single Shot
- 2 pulses = Burst Fire
- 3 pulses = Full Auto

If you don't like or want this, toggle off the Fire Mode Feedback switch.

**Note:** Fire mode switching is disabled in Haptic Experimental A and B modes (they auto-lock to Single Shot).

### Loading Custom Configs

1. Click **"Load Config"** in the GUI
2. Navigate to a config file (`.json`)
3. Select and open it
4. Settings will update immediately

### Saving Custom Configs

1. Adjust settings to your preference
2. Click **"Save Config As..."**
3. Choose a location and filename
4. Your custom config can be loaded later

---

## Troubleshooting

### Application Won't Start

**Issue:** Double-clicking the EXE does nothing or shows an error

**Solutions:**
- Make sure `ForceTubeVR_API_x64.dll` is in the same folder as the EXE files
- Check that ProTube hardware is connected
- Try running as Administrator: Right-click EXE → "Run as administrator"

### Bridge Won't Start

**Issue:** Clicking "Start Bridge" does nothing or shows an error

**Solutions:**
- Check that `ForceTubeVR_API_x64.dll` is present
- Make sure ProTube hardware is connected and powered on
- Close and restart the GUI application

### No Haptic Feedback

**Issue:** GUI shows bridge running, but no haptic feedback in VR

**Solutions:**
- Verify Bridge is running (green indicator in GUI)
- Check that Virtual Desktop is running and connected
- Ensure the modified DLL is installed correctly
- Try toggling modes in the GUI (real-time switching is now supported!)
- Verify your haptic mode selection matches your game type

### Wrong Haptics Coming Through

**Issue:** Getting damage kicks or unwanted haptics

**Solutions for Haptic Filtered:**
- Lower the Filter Intensity (try 40-60ms)
- Switch to Haptic Experimental A for better filtering

**Solutions for Experimental Modes:**
- Experimental A: Adjust Filter Intensity lower (40-60ms)
- Experimental B: This mode doesn't filter - switch to Experimental A if you need filtering

### Trigger Causing Unwanted Haptics

**Issue:** Aiming or left trigger causes unwanted kicks

**Solutions:**
- Use the **Ignore Left Hand** toggle to block left controller events
- Use the **Ignore Right Hand** toggle if right trigger causes issues

### Battery Shows "---%" 

**Issue:** Battery percentage not displaying

**Solution:**
- Some ProTube models don't support battery reporting
- This is normal and doesn't affect functionality

### Virtual Desktop Not Working / VR Issues

**Issue:** Virtual Desktop won't start or VR doesn't work correctly

**Solution - Restore Original DLL:**
1. Navigate to: `C:\Program Files\Virtual Desktop Streamer\OpenXR\`
2. Delete: `virtualdesktop-openxr.dll` (modified version)
3. Rename: `virtualdesktop-openxr.dll.backup` back to `virtualdesktop-openxr.dll`
4. Restart Virtual Desktop

### Settings Not Saving

**Issue:** Changes reset when closing the application

**Solutions:**
- Check that `protube_gui_config.json` exists in the Companion folder
- Make sure the folder isn't read-only
- Try running as Administrator

---

## Uninstallation

To completely remove ProTube OpenXR Companion:

### Step 1: Restore Original Virtual Desktop DLL

1. Navigate to: `C:\Program Files\Virtual Desktop Streamer\OpenXR\`
2. Delete: `virtualdesktop-openxr.dll` (modified version)
3. Rename: `virtualdesktop-openxr.dll.backup` to `virtualdesktop-openxr.dll`
4. Restart Virtual Desktop Streamer

### Step 2: Remove Companion Files

1. Delete folder: `C:\Users\[YOUR_USERNAME]\Documents\ProTube OpenXR Companion\`
2. Delete desktop shortcut (if created)

**Uninstallation Complete!**

---

## File Locations Reference

**Virtual Desktop DLL:**
- Location: `C:\Program Files\Virtual Desktop Streamer\OpenXR\`
- Modified file: `virtualdesktop-openxr.dll`
- Backup: `virtualdesktop-openxr.dll.backup`

**ProTube Companion:**
- Location: `C:\Users\[YOUR_USERNAME]\Documents\ProTube OpenXR Companion\`
- Main EXE: `ProTube OpenXR Companion.exe`
- Bridge EXE: `ProTube OpenXR Bridge.exe` (runs hidden - only launch from ProTube OpenXR Companion app)
- Config file: `protube_gui_config.json` (auto-created/updated)
- Driver config: `protube_config.txt` (auto-created by bridge, stored in Documents\ProTube OpenXR Companion)
- Battery file: `protube_battery.txt` (temporary, created by bridge)

---

## Advanced Configuration

### Game-Specific Profiles

The `OpenXR Companion Configs` folder contains game profiles. To use them:

1. Load the default config as a starting point
2. Adjust settings for your specific game
3. Save as a new config with the game name
4. Load this config when playing that game

### Fire Mode Recommendations

**Single Shot Mode:**
- Best for: Pistols, sniper rifles, shotguns
- Typical settings: High kick, medium rumble, short duration

**Burst Fire Mode:**
- Best for: Tactical rifles, burst weapons
- Typical settings: Medium kick, medium rumble, 3-shot burst

**Full Auto Mode:**
- Best for: Machine guns, SMGs, automatic rifles  
- Typical settings: Lower kick, higher rumble, fast fire rate

### Filter Intensity Guide

**For Haptic Filtered & Experimental A:**
- **30-40ms:** Ultra-tight, only immediate trigger-based haptics
- **40-60ms:** Balanced, blocks most damage (recommended starting point)
- **60-80ms:** Lenient, allows more haptics through
- **80-150ms:** Very lenient, minimal filtering

**Experimentation is key!** Different games send haptics at different timings.

---

## What's New in v1.01

- ✅ **Two new Experimental modes** (A: Filtered, B: Unfiltered)
- ✅ **Real-time mode switching** - no restart needed!
- ✅ **Ignore Right Hand toggle** - blocks right controller events
- ✅ **Config auto-reload** - changes apply within 500ms
- ✅ **Improved UI** - cleaner layout, better tooltips

---

## Credits

- ProTube VR hardware by ProTubeVR
- Virtual Desktop by Guy Godin
- OpenXR modifications for ProTube integration
- Community testing and feedback


