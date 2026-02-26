import time
import threading

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from ..base.db_interface import DBInterface


class DB(DBInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)

        self.pin = self.config.get("pin")
        self.is_on = False
        self._buzz_thread = None

        self.default_on_duration = self.config.get("on_duration", 0.3)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)

        self.log(f"Initializing REAL DB (Door Buzzer) on pin {self.pin}")

    def _buzz_loop(self):
        GPIO.output(self.pin, GPIO.HIGH)
        while self.is_on:
            time.sleep(0.1)
        GPIO.output(self.pin, GPIO.LOW)

    def on(self):
        if not self.is_on:
            self.is_on = True

            self.log("BUZZER ON 🔊 (real)")
            self.callback(self.config, self.is_on)

            self._buzz_thread = threading.Thread(target=self._buzz_loop, daemon=True)
            self._buzz_thread.start()
        else:
            self.log("BUZZER IS ALREADY ON")

    def off(self):
        if self.is_on:
            self.is_on = False

            if self._buzz_thread:
                self._buzz_thread.join(timeout=1.0)
                self._buzz_thread = None

            GPIO.output(self.pin, GPIO.LOW)
            self.callback(self.config, self.is_on)
            self.log("BUZZER OFF 🔇 (real)")
        else:
            GPIO.output(self.pin, GPIO.LOW)

    def beep(self, duration: float):
        self.is_on = True
        GPIO.output(self.pin, GPIO.HIGH)
        self.callback(self.config, self.is_on)

        self.log(f"BUZZER BEEP for {duration}s (real)")
        time.sleep(duration)

        self.off()

    def cleanup(self):
        self.off()
        GPIO.output(self.pin, GPIO.LOW)
        GPIO.cleanup(self.pin)
        self.log("Real DB GPIO cleaned up")