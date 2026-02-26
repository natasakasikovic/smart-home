import time
import threading

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None
    
from ..base.ds_interface import DSInterface

def loop(ds):
    ds.log("REAL DS loop started")

    while not ds.should_stop():
        state_change = ds.detect_state_change()

        if state_change is not None:
            ds.callback(state_change, ds.config)

        time.sleep(ds.config.get("poll_interval", 0.1))

    ds.cleanup()
    ds.log("REAL DS loop stopped")

class DS(DSInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)

        self.pin = self.config.get("pin")
        self.is_open = None
        self.last_change_time = 0
        self.debounce_time = self.config.get("debounce_ms", 50) / 1000.0  # ms to seconds

        self.log(
            f"Initializing REAL DS (Door Sensor) on pin {self.pin} with {self.debounce_time*1000}ms debounce"
        )

        try:
            GPIO.setmode(GPIO.BCM)
        except ValueError:
            pass
        
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def detect_state_change(self):
        button_state = GPIO.input(self.pin)
        current_state = button_state == GPIO.LOW
        
        if self.is_open is None:
            self.is_open = current_state
            self.last_change_time = time.time()
            self.log(f"Initial state: {'OPEN' if self.is_open else 'CLOSED'}")
            return None
        
        if current_state != self.is_open:
            current_time = time.time()
            
            if (current_time - self.last_change_time) < self.debounce_time:
                return None
            
            self.is_open = current_state
            self.last_change_time = current_time
            
            if self.is_open:
                self.log("DOOR OPENED (real)")
            else:
                self.log("DOOR CLOSED (real)")
            
            return self.is_open
        
        return None

    def start(self):
        thread = threading.Thread(
            target=loop,
            args=(self,),
            name=f"DS-{self.config.get('name', 'unknown')}",
            daemon=True
        )
        thread.start()
        self.log("REAL DS thread started")
        return thread

    def cleanup(self):
        self.log(f"Cleaning up GPIO pin {self.pin}")
        GPIO.cleanup(self.pin)

    def log(self, message: str) -> None:
        super().log(message)

    def should_stop(self):
        return super().should_stop()