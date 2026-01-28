import threading
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from ..base.dpir_interface import DPIRInterface


def loop(dpir):
    if GPIO is None:
        raise RuntimeError("RPi.GPIO not available")

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(dpir.pin, GPIO.IN)

    GPIO.add_event_detect(dpir.pin, GPIO.RISING, callback=lambda channel: dpir._motion_detected())

    try:
        while not dpir.should_stop():
            time.sleep(0.01)
    finally:
        GPIO.remove_event_detect(dpir.pin)
        GPIO.cleanup(dpir.pin)
        dpir.log("GPIO cleaned up for DPIR")


class DPIR(DPIRInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)

        if GPIO is None:
            raise RuntimeError("RPi.GPIO not available")

        self.pin = config["pin"]
        self._motion = False
        self.log(f"Initializing real DPIR on pin {self.pin}")

    def _motion_detected(self):
        self._motion = True
        self.log('Motion DETECTED (real)')
        if self.callback:
            self.callback(self.config)

    def detect_motion(self) -> bool:
        motion = self._motion
        self._motion = False 
        return motion

    def should_stop(self):
        return self.stop_event.is_set()

    def start(self):
        t = threading.Thread(target=loop, args=(self,), daemon=True)
        t.start()
        return t