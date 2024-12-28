# OBS-Progress-Bar-Hotkey-Plugin

> **Create a dynamic, hotkey-controlled progress bar in OBS!**  
> This Python script allows you to select an image or source within OBS and transform it into a customizable progress bar.  
> You can bind keys to increase, decrease, reset, or sustain the bar's visibility—with smooth animations and optional sound effects.

---

## Table of Contents

- [Features](#features)  
- [Requirements](#requirements)  
- [Installation](#installation)  
- [Configuration](#configuration)  
- [Usage](#usage)  
- [Hotkeys](#hotkeys)  
- [Animations & Sound Effects](#animations--sound-effects)  
- [Code Reference](#code-reference)  
- [License](#license)  

---

## Features

- **Progress Bar on Any Source**  
  Turn any image or visual source into a progress bar.

- **Smooth Animations**  
  Animations for increasing/decreasing progress, fading out, and resetting.

- **Visibility Control**  
  Fades out automatically when not used, or can be sustained via a hotkey.

- **Sound Effects**  
  Optional sound triggers for increase, decrease, reset, or full progress.

- **Container Opacity**  
  A separate container’s opacity is adjusted to match the bar’s visibility.

---

## Requirements

- **OBS Studio** (running in **normal mode**, not safe mode)  
- **Python 3** and [OBS Python scripting support](https://obsproject.com/docs/scripting.html)  
- **A media source** (optional) if you want sound effects to play

---

## Installation

1. **Download/Copy the Python Script**  
   Save the `progress_bar_script.py` (or however you've named it) on your system.

2. **Open OBS** in normal mode.  
   - Make sure you’re not in safe mode, as scripts are disabled there.

3. **Add the Script**  
   - Go to `Tools` → `Scripts` → `+` (Add script).
   - Select and load the Python script (`.py`).

Once the script is added, you can proceed to configure it in OBS.

---

## Configuration

1. **Open the Script Settings**  
   - In OBS, go to `Tools` → `Scripts`.  
   - Select the “OBS-Progress-Bar-Hotkey-Plugin” script in the list to reveal its properties.

2. **Select Progress Bar Source**  
   - Choose **any source** (e.g., an image or color block) to be your progress bar.

3. **(Optional) Add Container**  
   - If you have a decorative frame or container source, select it under **"Progress Bar Container"**.

4. **Choose Sound Sources** (optional)  
   - Assign existing audio or media sources for Increase, Decrease, Reset, and Full Progress.  
   - When the bar hits full or you trigger a hotkey, these will play if configured.

5. **Set Hotkeys**  
   - Go to `File` → `Settings` → `Hotkeys` in OBS.  
   - Scroll down to your script’s section and bind keys for:
     - **Increase Hotkey**  
     - **Decrease Hotkey**  
     - **Reset Hotkey**  
     - **Sustain Hotkey**

---

## Usage

1. **Increase/Decrease**  
   - Press your chosen **Increase** or **Decrease** hotkey to adjust the bar’s level.  
   - Each press moves the progress up or down by 1 level (up to a maximum).

2. **Reset**  
   - Press **Reset** to smoothly bring the bar back to 0.

3. **Sustain**  
   - Press **Sustain** to keep the bar visible indefinitely.  
   - Release the sustain hotkey (or press it again if you set a toggle) to allow automatic fade out.

4. **Fade Out**  
   - If neither sustain is active nor recent presses occurred, the bar will automatically fade out.

---

## Hotkeys

In the OBS `Hotkeys` menu, look for entries related to this script. By default, the script references:

- **Increase Level** (`ALT+1`)  
- **Decrease Level** (`ALT+2`)  
- **Sustain Visibility** (`ALT+3`)  
- **Reset Progress** (`ALT+4`)

> **Pro Tip**: You can customize these hotkeys however you like.  

---

## Animations & Sound Effects

- **Animations**  
  - The bar seamlessly transitions to new values using the configured duration.  
  - When idle, it fades out over a set period to keep your scene clear.

- **Sound Effects**  
  - If you’ve specified media sources for **Increase**, **Decrease**, **Reset**, or **Full**, they’ll play upon hotkey press or when the bar reaches max progress.  
  - Ensure the media source in OBS is set to a short audio clip or effect for the best user experience.

---

## Code Reference

Below is a condensed snippet of the main script. For a detailed view, refer to the file in this repository:

<details>
  <summary>Click to expand Python code reference</summary>

```python
import obspython as obs
import time
import threading
from threading import Thread, Event, Lock

class ProgressBar:
    def __init__(self):
        # Initialization
        self.progress_value = 0
        self.progress_target = 0
        self.source_name = ""
        self.visibility_event = Event()
        # ... [other class variables and locks]

    def get_source(self):
        """Get the OBS source by name with error handling."""
        # Implementation...

    def setup_filters(self, source):
        """Set up required filters with proper initialization."""
        # Implementation...

    def update_progress(self, progress, opacity=100.0):
        """Update filters with proper width calculation and error handling."""
        # Implementation...

    def fade_out(self):
        """Smooth opacity fade out with proper thread management."""
        # Implementation...

    # Additional methods for reset, sustain, animations, hotkey handling, etc.

# Global instance
progress_bar = ProgressBar()

def script_description():
    return "Progress Bar Controller with hotkeys (ALT+1, ALT+2, ALT+3, ALT+4)"

def script_properties():
    """Create script properties for OBS to display."""
    # Implementation...

def script_update(settings):
    """Update script settings from the user interface."""
    # Implementation...

def script_load(settings):
    """When the script is loaded, register hotkeys."""
    # Implementation...

def script_unload():
    """Clean up on script unload."""
    progress_bar.cleanup()
```
</details>

##  License

**MIT License**

  Feel free to use, modify, and distribute this plugin under the terms of the MIT License.
