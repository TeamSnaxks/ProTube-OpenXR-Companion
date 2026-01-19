# ProTube OpenXR Companion v1.01

Unofficial ProTube VR haptic feedback integration for Virtual Desktop OpenXR

---

## What's This?

Adds ProTube VR gun accessory support to Virtual Desktop, enabling:
- ✅ Realistic haptic feedback kick and rumble
- ✅ 4 haptic modes including 2 new Experimental modes
- ✅ 3 fire modes (Single, Burst, Full Auto)
- ✅ Customizable haptic strength and timing
- ✅ Real-time mode switching without restarting

---

## Quick Install

**3 Simple Steps:**

1. **Replace Virtual Desktop DLL** (in `Program Files\Virtual Desktop Streamer\OpenXR\`)
2. **Copy Companion folder** (to your Documents folder)
3. **Run the EXE** and click "Start Bridge"

See `INSTALLATION_GUIDE.md` for detailed step-by-step instructions.

---

## What's Included

📁 **DLL Folder**
- Modified Virtual Desktop OpenXR DLL with ProTube support

📁 **ProTube OpenXR Companion Folder**
- GUI Application (EXE) - Main interface
- Bridge Application (EXE) - Handles haptic feedback
- Configuration folder
- ForceTube API DLL

📄 **Documentation**
- `INSTALLATION_GUIDE.md` - Detailed instructions with troubleshooting

---

## Features

**Haptic Modes:**
- **Trigger** - Haptic from trigger pull (no game haptics needed)
- **Haptic Filtered** - Game haptics with damage filtering
- **Haptic Experimental A** - Filtered universal mode for complex games
- **Haptic Experimental B** - Unfiltered universal mode for max responsiveness

**Fire Modes:**
- Single Shot - One kick per trigger pull
- Burst Fire - Configurable burst count
- Full Auto - Continuous fire while trigger held

**Customization:**
- Kick strength (0-100%)
- Rumble intensity (0-100%)
- Kick duration (10-200ms)
- Fire rate for auto/burst modes
- Filter intensity (30-150ms) for filtered modes
- Latency compensation (0-100ms standard, 0-10ms for Experimental)

**Options:**
- Ignore left/right hand toggles
- Fire mode feedback toggle
- Battery monitoring
- Real-time settings changes
- Mode hot-switching (no restart needed!)

---

## In-Game Controls

**B Button (right controller):**
- Hold 1 second → Single Shot
- Double tap → Burst Fire
- Triple tap → Full Auto

You'll feel 1-3 haptic pulses confirming the mode.

**Note:** Fire mode switching is disabled in Experimental A & B modes (they auto-lock to Single Shot).

---

**Quick Guide:**
- 🎯 **No game haptics?** → Use **Trigger** mode
- 🎯 **Standard shooter with haptics?** → Use **Haptic Filtered** (Filter: 40-80ms)
- 🎯 **Complex haptics + need filtering?** → Use **Experimental A** (Filter: 40-80ms)
- 🎯 **No Filtering?** → Use **Experimental B** Use this mode in conjunction with Ignore Left/Right Hand. Works with certain games to remove unwanted hit damage haptics

---

## What's New in v1.01

- ✨ **Two new Experimental modes** (A: Filtered, B: Unfiltered)
- ✨ **Real-time mode switching** - change modes without restarting!
- ✨ **Ignore Right Hand toggle** - blocks right controller events
- ✨ **Config hot-reload** - changes apply within 500ms in-game
- ✨ **Improved UI** - cleaner layout, tighter spacing
- ✨ **Better tooltips** - clearer mode descriptions

---

## Requirements

- ✅ Windows 10 or 11
- ✅ Virtual Desktop / Virtual Desktop Streamer
- ✅ ProTube VR hardware (Tested with ProVolver Original)

---

## Support

**Need help?**
- Check `INSTALLATION_GUIDE.md` for detailed troubleshooting
- Review the Mode Selection Guide PDF
- Verify all files are in correct locations
- Make sure ProTube hardware is connected

**Common Issues:**
- **No haptics?** Check mode selection, verify Bridge is running
- **Getting damage kicks?** Lower Filter Intensity or switch to Experimental A
- **Unwanted haptics from aiming?** Enable Ignore Left Hand toggle

**To uninstall:**
1. Restore original Virtual Desktop DLL (rename `.backup` file)
2. Delete the Companion folder from Documents

---

## Credits

- ProTube VR hardware by ProTubeVR
- Virtual Desktop by Guy Godin  
- OpenXR integration modifications
- Community testing and feedback

---

## Disclaimer

This is an unofficial modification. Not affiliated with or endorsed by ProTubeVR or Virtual Desktop. All testing was done with a ProVolver (Original) unit.
Use at your own risk. Always backup original files before installation. 

Improper use of the haptic filter, shot duration and latency compensation options at their extremes can create unwanted repeat cycling of the device. Please understand what each does and how it relates to your game's haptics before setting. The red "STOP BRIDGE" doubles as a kill switch if needed.  

---

**Version:** 1.01  
**Last Updated:** January 2026
