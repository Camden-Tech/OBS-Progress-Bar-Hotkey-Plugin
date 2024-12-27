import obspython as obs
import time
import threading
from threading import Thread, Event, Lock


class ProgressBar:
    def __init__(self):
        self.progress_value = 0
        self.progress_target = 0
        self.source_name = ""
        self.visibility_event = Event()
        self.animation_lock = Lock()
        self.current_thread = None
        self.is_fading_out = False
        self.hotkeys = {}
        self.original_width = 0
        self.get_source_width()

        # Constants
        self.FADE_DURATION = 3.0
        self.RESIZE_DURATION = 1.0
        self.MAX_LEVELS = 10
        self.UPDATE_INTERVAL = 0.016  # ~60FPS

    def get_source(self):
        """Get the OBS source by name with error handling."""
        if not self.source_name:
            return None
        return obs.obs_get_source_by_name(self.source_name)

    def get_source_width(self):
        """
        Return the final scaled width (base_width + the Crop filter's right value),
        falling back to 0 if we can't get the source correctly.
        """
        source = self.get_source()
        if not source:
            return 0

        # 1) Get the base width
        base_width = obs.obs_source_get_width(source)
        if base_width == 1:
            base_width = 0

        # 2) Retrieve any existing "crop" filter
        crop_filter = obs.obs_source_get_filter_by_name(source, "crop")
        crop_right = 0
        if crop_filter:
            filter_settings = obs.obs_source_get_settings(crop_filter)
            crop_right = obs.obs_data_get_int(filter_settings, "right")
            obs.obs_data_release(filter_settings)
            obs.obs_source_release(crop_filter)

        # Add the crop’s "right" value to base_width
        base_width += crop_right

        obs.obs_source_release(source)

        # 4) Compute final scaled width
        scaled_width = int(base_width)

        # Cache this width internally
        self.original_width = scaled_width

        return scaled_width




    

    def setup_filters(self, source):
        """Set up required filters with proper initialization."""
        if not source:
            return False

        settings = obs.obs_data_create()
        try:
            # Set up Crop filter with full source width
            source_width = self.get_source_width()
            obs.obs_data_set_int(settings, "right", source_width)
            
            # Remove any existing filters to prevent duplicates
            existing_crop = obs.obs_source_get_filter_by_name(source, "crop")
            if existing_crop:
                obs.obs_source_filter_remove(source, existing_crop)
                obs.obs_source_release(existing_crop)

            existing_color = obs.obs_source_get_filter_by_name(source, "color_correction")
            if existing_color:
                obs.obs_source_filter_remove(source, existing_color)
                obs.obs_source_release(existing_color)

            # Create new filters
            crop_filter = obs.obs_source_create("crop_filter", "crop", settings, None)
            color_filter = obs.obs_source_create("color_filter", "color_correction", settings, None)

            if crop_filter and color_filter:
                obs.obs_source_filter_add(source, crop_filter)
                obs.obs_source_filter_add(source, color_filter)
                obs.obs_source_release(crop_filter)
                obs.obs_source_release(color_filter)
                return True
            return False
        finally:
            obs.obs_data_release(settings)
    def update_progress(self, progress, opacity=100.0):
        """
        Update filters with proper width calculation and error handling,
        clamping the crop to avoid flickering.
        """
        source = self.get_source()
        if not source:
            return

        source_width = self.original_width
        if source_width <= 0:
            # If width is still 0, do nothing
            obs.obs_source_release(source)
            return

        settings = obs.obs_data_create()
        try:
            # -------------------------
            # CHANGED LINES BELOW
            # -------------------------
            # Clamp progress in [0,1] just to be safe
            progress = max(0.0, min(progress, 1.0))

            crop_value = int((1 - progress) * source_width)

            # Make sure crop_value doesn’t exceed the scaled width or go negative
            crop_value = max(0, min(crop_value, source_width))
            

            crop = obs.obs_source_get_filter_by_name(source, "crop")
            if crop:
                obs.obs_data_set_int(settings, "right", crop_value)
                obs.obs_source_update(crop, settings)
                obs.obs_source_release(crop)

            color = obs.obs_source_get_filter_by_name(source, "color_correction")
            if color:
                obs.obs_data_set_double(settings, "opacity", opacity)
                obs.obs_source_update(color, settings)
                obs.obs_source_release(color)
        finally:
            obs.obs_data_release(settings)
            obs.obs_source_release(source)

    def animate(self, target_progress, duration):
        """Smoothly animate progress with proper thread management."""
        with self.animation_lock:
            # 1) Stop fade_out if it's active
            self.is_fading_out = False  

            # 2) Kill any old thread (if different)
            if self.current_thread and self.current_thread.is_alive():
                self.interrupt_animation()

            def animation_thread():
                start_time = time.time()
                start_progress = self.progress_value

                while time.time() - start_time < duration:
                    with self.animation_lock:
                        elapsed = time.time() - start_time
                        progress = min(1.0, elapsed / duration)
                        current = start_progress + (target_progress - start_progress) * progress
                        self.progress_value = current
                        self.update_progress(current / self.MAX_LEVELS, 100.0)
                    time.sleep(self.UPDATE_INTERVAL)

                # Snap to final
                self.progress_value = target_progress
                self.update_progress(target_progress / self.MAX_LEVELS, 100.0)

                # If user hasn’t asked to sustain, fade out
                if not self.visibility_event.is_set():
                    self.fade_out()

            # 3) Start the new animation thread
            self.current_thread = Thread(target=animation_thread)
            self.current_thread.start()


    def reset(self):
        """Reset progress with proper duration scaling."""
        with self.animation_lock:
        # Stop any fade_out in progress
            self.is_fading_out = False  # <--- ADD THIS
            
            if self.current_thread and self.current_thread.is_alive():
                self.interrupt_animation()

            reset_duration = self.RESIZE_DURATION * (self.progress_target / self.MAX_LEVELS)
            self.progress_target = 0

            def reset_thread():
                start_time = time.time()
                start_progress = self.progress_value

                while time.time() - start_time < reset_duration:
                    with self.animation_lock:
                        elapsed = time.time() - start_time
                        progress = min(1.0, elapsed / reset_duration)
                        current = start_progress * (1 - progress)
                        self.progress_value = current
                        self.update_progress(current / self.MAX_LEVELS, 100.0)
                    time.sleep(self.UPDATE_INTERVAL)

                self.progress_value = 0
                self.update_progress(0.0, 100.0)

                if not self.visibility_event.is_set():
                    self.fade_out()

            self.current_thread = Thread(target=reset_thread)
            self.current_thread.start()

    def fade_out(self):
        """Smooth opacity fade out with proper thread management."""
        with self.animation_lock:
            # 1) If we are already fading, skip
            if self.is_fading_out:
                return

            # 2) If there's a thread running, kill it (unless it's us)
            if (self.current_thread and 
                self.current_thread.is_alive() and
                self.current_thread is not threading.current_thread()):
                self.interrupt_animation()

            self.is_fading_out = True

            def fade_thread():
                start_time = time.time()

                while time.time() - start_time < self.FADE_DURATION and self.is_fading_out:
                    with self.animation_lock:
                        progress = (time.time() - start_time) / self.FADE_DURATION
                        opacity = max(0.0, 100.0 * (1 - progress))
                        self.update_progress(self.progress_value / self.MAX_LEVELS, opacity)
                    time.sleep(self.UPDATE_INTERVAL)

                # Final step: if we are still fading, set opacity to zero
                if self.is_fading_out:
                    self.update_progress(self.progress_value / self.MAX_LEVELS, 0.0)

                self.is_fading_out = False

            self.current_thread = Thread(target=fade_thread)
            self.current_thread.start()



    def sustain(self):
        """Keep the progress bar visible."""
        with self.animation_lock:
            # Stop any fade, kill old thread
            self.is_fading_out = False
            if self.current_thread and self.current_thread.is_alive():
                self.interrupt_animation()

        self.visibility_event.set()
        self.update_progress(self.progress_value / self.MAX_LEVELS, 100.0)

        def sustain_thread():
            # Keep refreshing visibility while set
            while self.visibility_event.is_set():
                with self.animation_lock:
                    self.update_progress(self.progress_value / self.MAX_LEVELS, 100.0)
                time.sleep(self.UPDATE_INTERVAL)

            # Once user stops sustaining, fade out
            self.fade_out()

        self.current_thread = Thread(target=sustain_thread)
        self.current_thread.start()

    def interrupt_animation(self):
        """Safely interrupt current animation (if it's another thread)."""
        if (self.current_thread and
            self.current_thread.is_alive() and
            self.current_thread is not threading.current_thread()):
            self.current_thread.join(timeout=0.1)

        self.current_thread = None


    def handle_hotkey(self, pressed, action):
        """Handle hotkey events with proper state management."""
        if not pressed:
            if action == "sustain":
                self.visibility_event.clear()
            return

        source = self.get_source()
        if not source:
            return
        obs.obs_source_release(source)

        self.visibility_event.clear()

        if action == "increase" and self.progress_target < self.MAX_LEVELS:
            self.progress_target += 1
            self.animate(self.progress_target, self.RESIZE_DURATION)
        elif action == "decrease" and self.progress_target > 0:
            self.progress_target -= 1
            self.animate(self.progress_target, self.RESIZE_DURATION)
        elif action == "sustain":
            self.sustain()
        elif action == "reset":
            self.reset()

    def cleanup(self):
        """Clean up resources properly."""
        self.visibility_event.clear()
        self.interrupt_animation()
        source = self.get_source()
        if source:
            obs.obs_source_release(source)
        self.hotkeys.clear()
        self.original_width = 0


# Global instance
progress_bar = ProgressBar()


def script_description():
    return "Progress Bar Controller with hotkeys (ALT+1: Increase, ALT+2: Decrease, ALT+3: Sustain, ALT+4: Reset)"


def script_properties():
    props = obs.obs_properties_create()
    p = obs.obs_properties_add_list(props, "source_name", "Select Source", 
                                  obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)
    obs.obs_property_list_add_string(p, "None", "")
    
    sources = obs.obs_enum_sources()
    if sources:
        for source in sources:
            name = obs.obs_source_get_name(source)
            obs.obs_property_list_add_string(p, name, name)
        obs.source_list_release(sources)
    
    return props


def script_update(settings):
    progress_bar.source_name = obs.obs_data_get_string(settings, "source_name")
    source = progress_bar.get_source()
    if source:
        progress_bar.setup_filters(source)
        progress_bar.update_progress(0.0, 0.0)
        obs.obs_source_release(source)


def script_load(settings):
    progress_bar.source_name = obs.obs_data_get_string(settings, "source_name")
    
    register_hotkeys()


def script_unload():
    progress_bar.cleanup()


def register_hotkeys():
    """Register all hotkeys with proper descriptions."""
    hotkey_names = {
        "increase": "Increase Level (ALT+1)",
        "decrease": "Decrease Level (ALT+2)",
        "sustain": "Sustain Visibility (ALT+3)",
        "reset": "Reset Progress (ALT+4)"
    }
    
    for action, description in hotkey_names.items():
        progress_bar.hotkeys[action] = obs.obs_hotkey_register_frontend(
            action, description,
            lambda pressed, act=action: progress_bar.handle_hotkey(pressed, act)
        )