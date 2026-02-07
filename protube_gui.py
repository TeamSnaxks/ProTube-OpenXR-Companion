import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import subprocess
import time
import sys

class IndicatorLight(tk.Canvas):
    """Small indicator light widget"""
    def __init__(self, parent, width=12, height=20, **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)
        self.configure(bg='#2b2b2b')
        self.state = "on"
        self.draw()
    
    def draw(self):
        self.delete("all")
        if self.state == "on":
            self.create_rectangle(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(), 
                                 fill="#90EE90", outline="")
        elif self.state == "off":
            self.create_rectangle(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(), 
                                 fill="#404040", outline="")
    
    def set_state(self, state):
        """Set state: 'on' or 'off'"""
        self.state = state
        self.draw()

class ToggleSwitch(tk.Canvas):
    """Custom toggle switch widget"""
    def __init__(self, parent, width=50, height=24, **kwargs):
        super().__init__(parent, width=width, height=height, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.is_on = True
        
        # Colors
        self.bg_on = "#90EE90"  # Lime green
        self.bg_off = "#404040"
        self.circle_color = "white"
        
        self.configure(bg='#2b2b2b')
        self.bind("<Button-1>", self.toggle)
        self.draw()
    
    def draw(self):
        self.delete("all")
        bg = self.bg_on if self.is_on else self.bg_off
        
        # Background pill
        self.create_oval(0, 0, self.height, self.height, fill=bg, outline="")
        self.create_oval(self.width-self.height, 0, self.width, self.height, fill=bg, outline="")
        self.create_rectangle(self.height/2, 0, self.width-self.height/2, self.height, fill=bg, outline="")
        
        # Circle
        circle_x = self.width - self.height/2 - 4 if self.is_on else self.height/2
        self.create_oval(circle_x-8, 4, circle_x+8, self.height-4, fill=self.circle_color, outline="")
    
    def toggle(self, event=None):
        self.is_on = not self.is_on
        self.draw()
        if hasattr(self, 'command') and self.command:
            self.command(self.is_on)
    
    def set(self, value):
        self.is_on = value
        self.draw()
    
    def get(self):
        return self.is_on

class ToolTip:
    """Tooltip widget"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
    
    def show(self, event=None):
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip, text=self.text, 
                        bg="#3a3a3a", fg="white", relief="solid", 
                        borderwidth=1, font=("Arial", 9), padx=8, pady=6,
                        justify='left')
        label.pack()
    
    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class ProTubeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ProTube OpenXR Companion")
        self.root.geometry("1450x540")
        
        # Dark theme colors
        self.bg_dark = "#2b2b2b"
        self.bg_panel = "#3a3a3a"
        self.lime_green = "#90EE90"
        self.text_white = "#ffffff"
        self.text_gray = "#b0b0b0"
        
        self.root.configure(bg=self.bg_dark)
        
        # Bridge process
        self.bridge_process = None
        
        # Storage for sliders and values (for dynamic updates)
        self.sliders = {}  # config_key -> slider widget
        self.value_vars = {}  # config_key -> StringVar
        
        # Config file
        self.config_file = "protube_gui_config.json"
        
        # Default values
        self.config = {
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
        
        # Load existing config if available
        self.load_default_config()
        
        # Build UI
        self.create_ui()
        
        # Apply visibility updates based on loaded config
        self.update_filter_visibility()
        self.update_fire_mode_visibility()
        self.update_latency_range()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Check if bridge is running
        self.check_bridge_status()
    
    def load_default_config(self):
        """Load config from default file on startup"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
                print(f"Loaded config from {self.config_file}")
            except Exception as e:
                print(f"Could not load config: {e}")
    
    def save_config_file(self):
        """Save current config to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"Config auto-saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def create_ui(self):
        """Create the entire UI"""
        
        # ===== HEADER =====
        header_frame = tk.Frame(self.root, bg=self.bg_dark)
        header_frame.pack(fill='x', padx=30, pady=12)
        
        title = tk.Label(header_frame, text="ProTube / Virtual Desktop OpenXR Companion", 
                        font=('Arial', 16, 'bold'), bg=self.bg_dark, fg=self.text_white)
        title.pack(side='left')
        
        subtitle = tk.Label(header_frame, text="(unofficial)", 
                           font=('Arial', 9), bg=self.bg_dark, fg=self.text_gray,
                           anchor='sw')  # Southwest anchor = bottom left
        subtitle.pack(side='left', padx=10, anchor='s')  # Anchor to bottom (south)
        
        # ===== BRIDGE CONTROL SECTION =====
        bridge_frame = tk.Frame(self.root, bg=self.bg_panel)
        bridge_frame.pack(fill='x', padx=30, pady=(0, 10))
        
        # Inner padding frame
        bridge_inner = tk.Frame(bridge_frame, bg=self.bg_panel)
        bridge_inner.pack(fill='x', padx=15, pady=10)
        
        # Bridge status label
        tk.Label(bridge_inner, text="Bridge Status:", font=('Arial', 10, 'bold'), 
                bg=self.bg_panel, fg=self.text_white).pack(side='left')
        
        # Status indicator
        self.bridge_status_light = IndicatorLight(bridge_inner, width=15, height=20, bg=self.bg_panel)
        self.bridge_status_light.set_state("off")
        self.bridge_status_light.pack(side='left', padx=(5, 15))
        
        # Status text
        self.bridge_status_text = tk.Label(bridge_inner, text="Not Running", 
                                          font=('Arial', 10), bg=self.bg_panel, fg=self.text_gray)
        self.bridge_status_text.pack(side='left', padx=(0, 20))
        
        # Battery indicator
        tk.Label(bridge_inner, text="Battery:", font=('Arial', 10, 'bold'), 
                bg=self.bg_panel, fg=self.text_white).pack(side='left', padx=(10, 5))
        
        self.battery_text = tk.Label(bridge_inner, text="---%", 
                                     font=('Arial', 10), bg=self.bg_panel, fg=self.text_gray)
        self.battery_text.pack(side='left', padx=(0, 20))
        
        # Battery file for reading from bridge
        self.battery_file = "protube_battery.txt"
        
        # Start/Stop button
        self.bridge_button = tk.Button(bridge_inner, text="Start Bridge", 
                                      font=('Arial', 10, 'bold'), bg=self.lime_green, fg='black',
                                      activebackground="#7FD87F", relief='flat',
                                      padx=20, pady=5, command=self.toggle_bridge)
        self.bridge_button.pack(side='left', padx=5)
        
        # Info label
        info_label = tk.Label(bridge_inner, 
                            text="Bridge reads config automatically - changes apply within 1 second", 
                            font=('Arial', 8), bg=self.bg_panel, fg=self.text_gray, 
                            anchor='e')
        info_label.pack(side='right', padx=10)
        
        # ===== TOP CONTROLS =====
        control_frame = tk.Frame(self.root, bg=self.bg_dark)
        control_frame.pack(fill='x', padx=30, pady=(0, 10))
        
        # Mode Select
        tk.Label(control_frame, text="Haptic Mode Select:", font=('Arial', 10), 
                bg=self.bg_dark, fg=self.text_white).pack(side='left', padx=(0, 10))
        
        # Container for dropdown + indicator
        dropdown_container = tk.Frame(control_frame, bg=self.bg_dark)
        dropdown_container.pack(side='left')
        
        self.mode_var = tk.StringVar(value=self.config["mode_select"])
        self.mode_var.trace('w', lambda *args: self.on_mode_change())
        mode_menu = tk.OptionMenu(dropdown_container, self.mode_var, 
                                  "Trigger", "Haptic Filtered", "Haptic Experimental A", "Haptic Experimental B")
        mode_menu.config(bg=self.bg_panel, fg=self.text_white, 
                        activebackground=self.lime_green, highlightthickness=0,
                        height=1)
        mode_menu.pack(side='left')
        
        # Indicator light
        mode_indicator = IndicatorLight(dropdown_container, width=15, height=24, bg=self.bg_dark)
        mode_indicator.pack(side='left', padx=(2, 30))
        
        # Tooltips
        ToolTip(mode_menu, 
                "Trigger: Haptic generated from Trigger Pull.\n"
                "Choose if game lacks haptics, or if you want a simplified experience.\n\n"
                "Haptic Filtered: Haptic From Game.\nChoose this if game has haptic support.\n"
                "Damage hits are filtered out so only shots kick the haptic module.\n"
                "Ammo out should also stop haptics\n"
                "(*except for Full Auto ammo out, if emptying entire clip with one trigger pull)\n\n"
                "Haptic Experimental A: Universal Mode (Filtered).\n"
                "Uses trigger-based filtering to block damage haptics.\n"
                "Best for games with complex haptics/kicks for every shot fired.\n\n"
                "Haptic Experimental B: Universal Mode (Unfiltered).\n"
                "Forwards all game haptics directly - no filtering.\n"
                "Auto-detects weapon fire rate and ammo out.")
        
        # Fire Mode Feedback toggle (store references for visibility control)
        self.feedback_label = tk.Label(control_frame, text="Fire Mode Feedback:", font=('Arial', 10), 
                bg=self.bg_dark, fg=self.text_white)
        self.feedback_label.pack(side='left', padx=(20, 10))
        
        self.feedback_toggle = ToggleSwitch(control_frame, width=50, height=24, bg=self.bg_dark)
        self.feedback_toggle.set(self.config["feedback"])
        self.feedback_toggle.command = lambda v: self.on_config_change()
        self.feedback_toggle.pack(side='left')
        
        self.feedback_tooltip = ToolTip(self.feedback_toggle,
                "Light kick feedback after selecting fire modes.\n"
                "Single: One kick\nBurst: Two kicks\nFull Auto: Three kicks")
        
        # Ignore Left Hand toggle
        self.ignore_left_label = tk.Label(control_frame, text="Ignore Left Hand:", font=('Arial', 10), 
                bg=self.bg_dark, fg=self.text_white)
        self.ignore_left_label.pack(side='left', padx=(20, 10))
        
        self.ignore_left_toggle = ToggleSwitch(control_frame, width=50, height=24, bg=self.bg_dark)
        self.ignore_left_toggle.set(self.config["ignore_left_hand"])
        self.ignore_left_toggle.command = lambda v: self.on_config_change()
        self.ignore_left_toggle.pack(side='left')
        
        ToolTip(self.ignore_left_toggle,
                "Block all left hand trigger/haptic events.\n"
                "Useful for games that send unwanted haptics\n"
                "when left trigger is pulled (e.g., aiming).")
        
        # Ignore Right Hand toggle
        tk.Label(control_frame, text="Ignore Right Hand:", font=('Arial', 10), 
                bg=self.bg_dark, fg=self.text_white).pack(side='left', padx=(20, 10))
        
        self.ignore_right_toggle = ToggleSwitch(control_frame, width=50, height=24, bg=self.bg_dark)
        self.ignore_right_toggle.set(self.config.get("ignore_right_hand", False))
        self.ignore_right_toggle.command = lambda v: self.on_config_change()
        self.ignore_right_toggle.pack(side='left')
        
        ToolTip(self.ignore_right_toggle,
                "Block all right hand trigger/haptic events.\n"
                "Useful for games that send unwanted haptics\n"
                "when right trigger is pulled.")
        
        # ===== FILTER INTENSITY (only for Haptic Filtered mode) - AFTER Fire Mode Feedback =====
        self.filter_container = tk.Frame(control_frame, bg=self.bg_dark)
        
        tk.Label(self.filter_container, text="Filter Intensity (ms):", 
                font=('Arial', 10), bg=self.bg_dark, fg=self.text_white).pack(side='left', padx=(20, 10))
        
        self.filter_slider = tk.Scale(self.filter_container, from_=30, to=150, orient='horizontal',
                                resolution=1, showvalue=0, bg=self.bg_dark, fg=self.text_white,
                                troughcolor=self.lime_green, highlightthickness=0, 
                                length=300, sliderlength=20, bd=0)
        self.filter_slider.set(self.config.get("filter_window_ms", 60))
        self.filter_slider.pack(side='left', padx=(0, 10))
        
        self.filter_value = tk.StringVar(value=str(self.config.get("filter_window_ms", 60)))
        filter_entry = tk.Entry(self.filter_container, textvariable=self.filter_value, 
                               font=('Arial', 9, 'bold'), bg=self.bg_panel, 
                               fg=self.lime_green, width=5, justify='center',
                               highlightthickness=1, highlightbackground=self.lime_green,
                               insertbackground=self.lime_green)
        filter_entry.pack(side='left')
        
        self.filter_slider.config(command=lambda v: self.on_slider_change("filter_window_ms", v, self.filter_value, self.filter_slider))
        filter_entry.bind('<Return>', lambda e: self.on_entry_change("filter_window_ms", self.filter_value, self.filter_slider, 30, 150))
        filter_entry.bind('<FocusOut>', lambda e: self.on_entry_change("filter_window_ms", self.filter_value, self.filter_slider, 30, 150))
        
        ToolTip(self.filter_slider,
                "Filter time window in milliseconds.\n"
                "Lower = More strict (filters more)\n"
                "Higher = Less strict (lets more through)")
        
        # Show/hide based on initial mode
        self.update_filter_visibility()
        
        # ===== SECTION TITLE =====
        section_title_frame = tk.Frame(self.root, bg=self.bg_dark)
        section_title_frame.pack(fill='x', padx=30, pady=(15, 10))
        
        section_title = tk.Label(section_title_frame, text="Shot Customization", 
                                font=('Arial', 14, 'bold'), bg=self.bg_dark, fg=self.text_white)
        section_title.pack(side='left')
        
        # Horizontal separator line
        separator = tk.Frame(section_title_frame, bg='#ffffff', height=1)
        separator.pack(side='left', fill='x', expand=True, padx=(15, 0))
        
        # ===== MAIN CONTENT =====
        main_frame = tk.Frame(self.root, bg=self.bg_dark)
        main_frame.pack(fill='both', expand=True, padx=30, pady=(0, 10))
        
        # Configure grid with column gaps
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        
        # Add uniform gap between columns
        main_frame.grid_columnconfigure(0, pad=0)
        main_frame.grid_columnconfigure(1, pad=0)
        main_frame.grid_columnconfigure(2, pad=0)
        
        # Three mode panels - custom padding for each
        self.single_panel = self.create_mode_panel(main_frame, "single", "Single Shot", 0, padx=(0, 12))
        self.burst_panel = self.create_mode_panel(main_frame, "burst", "Burst Fire", 1, padx=(12, 12))
        self.auto_panel = self.create_mode_panel(main_frame, "auto", "Full Auto", 2, padx=(12, 0))
        
        # ===== LATENCY CONTROL =====
        latency_outer = tk.Frame(self.root, bg=self.bg_dark)
        latency_outer.pack(fill='x', padx=30, pady=(15, 0))
        
        # Center container
        latency_frame = tk.Frame(latency_outer, bg=self.bg_dark)
        latency_frame.pack(anchor='center')
        
        tk.Label(latency_frame, text="Latency Compensation (ms):", 
                font=('Arial', 10), bg=self.bg_dark, fg=self.text_white).pack(side='left', padx=(0, 10))
        
        latency_slider = tk.Scale(latency_frame, from_=0, to=100, orient='horizontal',
                                 resolution=1, showvalue=0, bg=self.bg_dark, fg=self.text_white,
                                 troughcolor=self.lime_green, highlightthickness=0, 
                                 length=300, sliderlength=20, bd=0)
        latency_slider.set(self.config["latency"])
        latency_slider.pack(side='left', padx=(0, 10))
        
        # Store reference for mode-based range updates
        self.latency_slider = latency_slider
        
        latency_value = tk.StringVar(value=str(self.config["latency"]))
        self.latency_value_var = latency_value
        latency_entry = tk.Entry(latency_frame, textvariable=latency_value, 
                                font=('Arial', 9, 'bold'), bg=self.bg_panel, 
                                fg=self.lime_green, width=5, justify='center',
                                highlightthickness=1, highlightbackground=self.lime_green,
                                insertbackground=self.lime_green)
        latency_entry.pack(side='left')
        
        latency_slider.config(command=lambda v: self.on_latency_change(v))
        latency_entry.bind('<Return>', lambda e: self.on_latency_entry_change())
        latency_entry.bind('<FocusOut>', lambda e: self.on_latency_entry_change())
        
        ToolTip(latency_slider,
                "Adds latency to kick to align better with visuals.\n"
                "Look at Virtual Desktop's Latency and adjust\naccordingly to make shots tighter.")
        
        # ===== BUTTON FRAME =====
        button_frame = tk.Frame(self.root, bg=self.bg_dark)
        button_frame.pack(pady=(10, 20))
        
        # Load button
        load_btn = tk.Button(button_frame, text="Load Config", 
                            font=('Arial', 11, 'bold'), bg=self.bg_panel, fg=self.text_white,
                            activebackground=self.lime_green, relief='flat',
                            padx=25, pady=5, command=self.load_config)
        load_btn.pack(side='left', padx=5)
        
        # Save button
        save_btn = tk.Button(button_frame, text="Save Config As...", 
                            font=('Arial', 11, 'bold'), bg=self.lime_green, fg='black',
                            activebackground="#7FD87F", relief='flat',
                            padx=25, pady=5, command=self.save_config)
        save_btn.pack(side='left', padx=5)
        
    def create_mode_panel(self, parent, mode, title, column, padx=(6, 6)):
        """Create a panel with horizontal sliders for a fire mode"""
        panel = tk.Frame(parent, bg=self.bg_panel)
        panel.grid(row=0, column=column, padx=padx, sticky='nsew')
        
        # Title
        title_label = tk.Label(panel, text=title, font=('Arial', 12, 'bold'), 
                              bg=self.bg_panel, fg=self.text_white)
        title_label.pack(pady=(20, 18))  # Increased from (10, 12)
        
        # Sliders container
        sliders_container = tk.Frame(panel, bg=self.bg_panel)
        sliders_container.pack(fill='both', expand=True, padx=12, pady=(0, 20))  # Increased from (0, 10)
        
        # Sliders data
        sliders_data = [
            ("Kick Strength (%)", f"{mode}_kick", 0, 100),
            ("Rumble Strength (%)", f"{mode}_rumble", 0, 100),
            ("Duration (ms)", f"{mode}_duration", 10, 200)
        ]
        
        if mode == "burst":
            sliders_data.append(("Burst Count", f"{mode}_count", 1, 5))
        
        if mode == "auto":
            sliders_data.append(("Fire Rate (ms)", f"{mode}_rate", 30, 150))
        
        for idx, (label_text, config_key, min_val, max_val) in enumerate(sliders_data):
            self.create_horizontal_slider(sliders_container, label_text, config_key, min_val, max_val, idx)
        
        return panel  # Return panel reference for visibility control
    
    def create_horizontal_slider(self, parent, label, config_key, min_val, max_val, row):
        """Create a horizontal slider with label and editable value field"""
        container = tk.Frame(parent, bg=self.bg_panel)
        container.pack(fill='x', pady=5)
        
        # Label
        label_widget = tk.Label(container, text=label, font=('Arial', 9), 
                               bg=self.bg_panel, fg=self.text_white, width=16, anchor='w')
        label_widget.pack(side='left')
        
        # Value entry
        value_var = tk.StringVar(value=str(self.config[config_key]))
        value_entry = tk.Entry(container, textvariable=value_var, 
                              font=('Arial', 9, 'bold'), bg=self.bg_panel, 
                              fg=self.lime_green, width=5, justify='center',
                              highlightthickness=1, highlightbackground=self.lime_green,
                              insertbackground=self.lime_green)
        value_entry.pack(side='right', padx=(5, 0))
        
        # Slider
        slider = tk.Scale(container, from_=min_val, to=max_val, orient='horizontal',
                         resolution=1, showvalue=0, bg=self.bg_panel, fg=self.text_white,
                         troughcolor=self.lime_green, highlightthickness=0, 
                         length=120, sliderlength=16, bd=0)
        slider.set(self.config[config_key])
        slider.pack(side='left', padx=8, fill='x', expand=True)
        
        # Store references for later updates
        self.sliders[config_key] = slider
        self.value_vars[config_key] = value_var
        
        # Bind events
        slider.config(command=lambda v: self.on_slider_change(config_key, v, value_var, slider))
        value_entry.bind('<Return>', lambda e: self.on_entry_change(config_key, value_var, slider, min_val, max_val))
        value_entry.bind('<FocusOut>', lambda e: self.on_entry_change(config_key, value_var, slider, min_val, max_val))
    
    def on_slider_change(self, config_key, value, value_var, slider):
        """Handle slider changes"""
        int_value = int(float(value))
        self.config[config_key] = int_value
        value_var.set(str(int_value))
        self.on_config_change()
    
    def on_entry_change(self, config_key, value_var, slider, min_val, max_val):
        """Handle manual entry changes"""
        try:
            int_value = int(value_var.get())
            int_value = max(min_val, min(max_val, int_value))
            self.config[config_key] = int_value
            value_var.set(str(int_value))
            slider.set(int_value)
            self.on_config_change()
            # Remove focus from entry to hide cursor
            self.root.focus()
        except ValueError:
            value_var.set(str(self.config[config_key]))
            self.root.focus()
    
    def update_filter_visibility(self):
        """Show or hide filter slider based on current mode"""
        if self.config["mode_select"] in ["Haptic Filtered", "Haptic Experimental A"]:
            self.filter_container.pack(side='left', padx=(10, 0))
        else:
            self.filter_container.pack_forget()
    
    def update_fire_mode_visibility(self):
        """Show or hide fire mode panels based on selected mode"""
        if self.config["mode_select"] in ["Haptic Experimental A", "Haptic Experimental B"]:
            # Experimental modes: Show only Single Shot, center it
            self.burst_panel.grid_forget()
            self.auto_panel.grid_forget()
            self.single_panel.grid(row=0, column=1, padx=20, sticky='nsew')  # Center column
            # Hide Fire Mode Feedback toggle (irrelevant for locked Single Shot)
            self.feedback_label.pack_forget()
            self.feedback_toggle.pack_forget()
        else:
            # Other modes: Show all three panels
            self.single_panel.grid(row=0, column=0, padx=(0, 12), sticky='nsew')
            self.burst_panel.grid(row=0, column=1, padx=(12, 12), sticky='nsew')
            self.auto_panel.grid(row=0, column=2, padx=(12, 0), sticky='nsew')
            # Show Fire Mode Feedback toggle (before Ignore Left to maintain order)
            self.feedback_label.pack(side='left', padx=(20, 10), before=self.ignore_left_label)
            self.feedback_toggle.pack(side='left', before=self.ignore_left_label)
    
    def on_mode_change(self):
        """Handle mode dropdown change"""
        self.config["mode_select"] = self.mode_var.get()
        self.update_filter_visibility()
        self.update_fire_mode_visibility()
        self.update_latency_range()
        
        # Auto-switch to Single Shot mode when Experimental A or B is selected
        if self.config["mode_select"] in ["Haptic Experimental A", "Haptic Experimental B"]:
            self.send_fire_mode_to_bridge("single")
        
        self.save_config_file()
    
    def send_fire_mode_to_bridge(self, mode):
        """Send fire mode change to Bridge via UDP"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = f"mode:{mode}"
            sock.sendto(message.encode('utf-8'), ("127.0.0.1", 5015))
            sock.close()
            print(f"[GUI] Sent fire mode to Bridge: {mode}")
        except Exception as e:
            print(f"[GUI] Could not send fire mode: {e}")
    
    def update_latency_range(self):
        """Update latency slider range based on selected mode"""
        if self.config["mode_select"] in ["Haptic Experimental A", "Haptic Experimental B"]:
            # Experimental A and B modes: 0-10ms only
            self.latency_slider.config(to=10)
            # Clamp current value if needed
            if self.config["latency"] > 10:
                self.config["latency"] = 10
                self.latency_slider.set(10)
                self.latency_value_var.set("10")
        else:
            # Other modes: 0-100ms
            self.latency_slider.config(to=100)
    
    def on_latency_change(self, value):
        """Handle latency slider changes"""
        int_value = int(float(value))
        self.config["latency"] = int_value
        self.latency_value_var.set(str(int_value))
        self.on_config_change()
    
    def on_latency_entry_change(self):
        """Handle latency entry changes"""
        try:
            int_value = int(self.latency_value_var.get())
            max_val = 10 if self.config["mode_select"] in ["Haptic Experimental A", "Haptic Experimental B"] else 100
            int_value = max(0, min(max_val, int_value))
            self.config["latency"] = int_value
            self.latency_value_var.set(str(int_value))
            self.latency_slider.set(int_value)
            self.on_config_change()
            self.root.focus()
        except ValueError:
            self.latency_value_var.set(str(self.config["latency"]))
            self.root.focus()
    
    def on_config_change(self):
        """Called whenever any config value changes - auto-save"""
        # Update config from UI
        self.config["mode_select"] = self.mode_var.get()
        self.config["feedback"] = self.feedback_toggle.get()
        self.config["ignore_left_hand"] = self.ignore_left_toggle.get()
        self.config["ignore_right_hand"] = self.ignore_right_toggle.get()
        
        # Show/hide filter slider based on mode
        self.update_filter_visibility()
        
        # Auto-save to file
        self.save_config_file()
    
    def check_bridge_status(self):
        """Check if bridge process is running and read battery status"""
        if self.bridge_process and self.bridge_process.poll() is None:
            # Bridge is running
            self.bridge_status_light.set_state("on")
            self.bridge_status_text.config(text="Running", fg=self.lime_green)
            self.bridge_button.config(text="Stop Bridge", bg="#FF6B6B")
            
            # Try to read battery status from file
            self.read_battery_status()
        else:
            # Bridge is not running
            self.bridge_status_light.set_state("off")
            self.bridge_status_text.config(text="Not Running", fg=self.text_gray)
            self.bridge_button.config(text="Start Bridge", bg=self.lime_green)
            self.battery_text.config(text="---%", fg=self.text_gray)
        
        # Check again in 1 second
        self.root.after(1000, self.check_bridge_status)
    
    def read_battery_status(self):
        """Read battery percentage from bridge-created file"""
        try:
            if os.path.exists(self.battery_file):
                with open(self.battery_file, 'r') as f:
                    battery_str = f.read().strip()
                    battery_pct = int(battery_str)
                    
                    # Color code based on battery level
                    if battery_pct > 50:
                        color = self.lime_green
                    elif battery_pct > 20:
                        color = "#FFA500"  # Orange
                    else:
                        color = "#FF6B6B"  # Red
                    
                    self.battery_text.config(text=f"{battery_pct}%", fg=color)
            else:
                self.battery_text.config(text="---%", fg=self.text_gray)
        except:
            self.battery_text.config(text="---%", fg=self.text_gray)
    
    def toggle_bridge(self):
        """Start or stop the bridge process"""
        if self.bridge_process is None or self.bridge_process.poll() is not None:
            self.start_bridge()
        else:
            self.stop_bridge()
    
    def start_bridge(self):
        """Start the bridge process"""
        try:
            # Check if bridge is already running
            if self.bridge_process and self.bridge_process.poll() is None:
                print("Bridge is already running")
                return
            
            # Try to find the bridge executable first (for EXE distribution)
            bridge_exe = "ProTube OpenXR Bridge.exe"
            bridge_script = "protube_bridge_with_gui_control.py"
            
            # Check for EXE first, then fall back to Python script
            if os.path.exists(bridge_exe):
                # Use the EXE (for distribution)
                # Note: Don't use CREATE_NEW_CONSOLE for windowed apps
                self.bridge_process = subprocess.Popen(
                    [bridge_exe],
                    creationflags=0 if os.name == 'nt' else 0
                )
                print(f"Bridge started (EXE, PID: {self.bridge_process.pid})")
            elif os.path.exists(bridge_script):
                # Use Python script (for development)
                self.bridge_process = subprocess.Popen(
                    ["python", bridge_script],
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                print(f"Bridge started (Python, PID: {self.bridge_process.pid})")
            else:
                messagebox.showerror("Error", 
                    f"Bridge not found!\n\n"
                    f"Looking for:\n"
                    f"  - {bridge_exe}\n"
                    f"  - {bridge_script}\n\n"
                    "Make sure the bridge is in the same directory as this GUI.")
                return
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start bridge:\n{str(e)}")
    
    def stop_bridge(self):
        """Stop the bridge process"""
        stopped = False
        
        try:
            if self.bridge_process:
                # Try graceful termination first
                self.bridge_process.terminate()
                try:
                    self.bridge_process.wait(timeout=2.0)
                    print("Bridge stopped gracefully")
                    stopped = True
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't stop
                    self.bridge_process.kill()
                    try:
                        self.bridge_process.wait(timeout=1.0)
                        print("Bridge force killed")
                        stopped = True
                    except:
                        print("Bridge didn't respond to kill signal")
                
                self.bridge_process = None
            
            # NUCLEAR OPTION: Use taskkill to ensure ALL Bridge instances are dead
            if os.name == 'nt':  # Windows only
                try:
                    result = subprocess.run(
                        ['taskkill', '/F', '/IM', 'ProTube OpenXR Bridge.exe'],
                        capture_output=True,
                        timeout=3,
                        text=True
                    )
                    if "SUCCESS" in result.stdout:
                        print("Killed remaining Bridge processes via taskkill")
                        stopped = True
                    elif "not found" not in result.stderr.lower():
                        print(f"Taskkill output: {result.stdout}")
                except Exception as e:
                    print(f"Taskkill failed: {e}")
            
            # Clean up battery file to prevent stale data
            try:
                if os.path.exists(self.battery_file):
                    os.remove(self.battery_file)
                    print("Cleaned up battery file")
            except Exception as e:
                print(f"Could not remove battery file: {e}")
            
            if stopped or not self.bridge_process:
                print("Bridge stop complete")
            else:
                print("Warning: Could not confirm bridge was stopped")
                
        except Exception as e:
            print(f"Error stopping bridge: {e}")
            # Try to clean up the handle anyway
            if self.bridge_process:
                try:
                    self.bridge_process.kill()
                except:
                    pass
                self.bridge_process = None
    
    def save_config(self):
        """Save configuration to a custom file"""
        filename = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.getcwd()
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.config, f, indent=4)
                messagebox.showinfo("Success", f"Configuration saved to:\n{os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")
    
    def load_config(self):
        """Load configuration from a custom file"""
        print("Load config button clicked")
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.getcwd()
        )
        
        print(f"Selected file: {filename}")
        
        if filename:
            try:
                print(f"Loading config from: {filename}")
                with open(filename, 'r') as f:
                    loaded_config = json.load(f)
                
                print(f"Loaded config: {loaded_config}")
                
                # Update config
                self.config.update(loaded_config)
                
                # Refresh all GUI widgets with new values
                self.refresh_gui_from_config()
                
                # Save to default config file
                self.save_config_file()
                
                # Show success message
                messagebox.showinfo("Config Loaded", 
                    f"Configuration loaded from:\n{os.path.basename(filename)}\n\n"
                    "All values have been updated!",
                    icon='info')
                
            except Exception as e:
                print(f"Error loading config: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to load:\n{str(e)}")
    
    def refresh_gui_from_config(self):
        """Refresh all GUI widgets from current config values"""
        try:
            # Update mode dropdown
            self.mode_var.set(self.config["mode_select"])
            self.update_filter_visibility()
            
            # Update feedback toggle
            self.feedback_toggle.set(self.config["feedback"])
            
            # Update ignore left hand toggle
            self.ignore_left_toggle.set(self.config["ignore_left_hand"])
            
            # Update all sliders and their value displays
            for config_key in self.sliders:
                if config_key in self.config:
                    # Update slider position
                    self.sliders[config_key].set(self.config[config_key])
                    # Update value display
                    self.value_vars[config_key].set(str(self.config[config_key]))
            
            print("GUI refreshed - all values updated!")
            
        except Exception as e:
            print(f"Error refreshing GUI: {e}")
            import traceback
            traceback.print_exc()
    
    def on_closing(self):
        """Handle window close event"""
        # Stop bridge if running
        if self.bridge_process and self.bridge_process.poll() is None:
            self.stop_bridge()
            # Give bridge a moment to fully terminate and release files
            time.sleep(0.5)
        
        # Destroy window
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProTubeGUI(root)
    root.mainloop()
