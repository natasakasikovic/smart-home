import threading
import time

class KitchenTimerService:
    def __init__(self, mqtt_publish_fn=None):
        self._mqtt_publish = mqtt_publish_fn  # mqtt_listener.publish
        self._lock = threading.Lock()
        self._total_seconds = 0
        self._running = False
        self._blinking = False
        self._btn_add_seconds = 10
    
    def set_mqtt_publish(self, fn):
        self._mqtt_publish = fn
    
    def _publish_display(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        value = f"{mins:02d}{secs:02d}"
        if self._mqtt_publish:
            self._mqtt_publish("commands/4sd", {
                "action": "display_time",
                "params": {"value": value}
            })
    
    def set_timer(self, seconds):
        with self._lock:
            self._total_seconds = seconds
            self._running = False
            self._blinking = False
        self._publish_display(seconds)
    
    def start(self):
        with self._lock:
            if self._blinking:
                self._blinking = False
                self._running = False
                return
            if self._running:
                return
            self._running = True
        threading.Thread(target=self._countdown_loop, daemon=True).start()
    
    def stop(self):
        with self._lock:
            self._running = False
            self._blinking = False
        with self._lock:
            s = self._total_seconds
        self._publish_display(s)
    
    def add_seconds(self, n):
        with self._lock:
            if self._blinking:
                self._blinking = False
                self._running = False
                return
            self._total_seconds += n
            s = self._total_seconds
        self._publish_display(s)
    
    def configure_btn(self, add_seconds):
        self._btn_add_seconds = add_seconds
    
    def on_btn_press(self):
        with self._lock:
            blinking = self._blinking
            running = self._running
        
        if blinking:
            self.stop()
        elif running:
            self.add_seconds(self._btn_add_seconds)
        else:
            print("[TIMER] BTN pressed but timer is not running, ignoring")
    
    def _countdown_loop(self):
        while True:
            with self._lock:
                if not self._running:
                    break
                if self._total_seconds <= 0:
                    self._running = False
                    self._blinking = True
                    break
                self._total_seconds -= 1
                s = self._total_seconds
            self._publish_display(s)
            time.sleep(1)
        
        with self._lock:
            should_blink = self._blinking
        if should_blink:
            self._blink_loop()
    
    def _blink_loop(self):
        visible = True
        while True:
            with self._lock:
                if not self._blinking:
                    break
            if self._mqtt_publish:
                if visible:
                    self._mqtt_publish("commands/4sd", {"action": "display_time", "params": {"value": "0000"}})
                else:
                    self._mqtt_publish("commands/4sd", {"action": "clear", "params": {}})
            visible = not visible
            time.sleep(0.5)