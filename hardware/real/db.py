import time
import threading

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from ..base.db_interface import DBInterface


def loop(db):
    db.log("Real DB loop started (idle)")
    while not db.should_stop():
        time.sleep(0.1) # do i need loop for door buzzer?
    db.log("Real DB loop stopped")


class DB(DBInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.log(
            "Initializing REAL DB (Door Buzzer) on pin {}".format(self.pin)
        )

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)
        self.log("BUZZER ON 🔊 (real)")

    def off(self):
        GPIO.output(self.pin, GPIO.LOW)
        self.log("BUZZER OFF 🔇 (real)")

    def beep(self, duration: float):
        self.on()
        time.sleep(duration)
        self.off()
        self.log(f"BUZZER BEEP for {duration}s (real)")

    def cleanup(self):
        GPIO.cleanup(self.pin)
        self.log("Real DB GPIO cleaned up")

    def start(self):
        thread = threading.Thread(
            target=loop,
            args=(self,),
            name=f"DB-{self.config.get('name', 'unknown')}",
            daemon=True
        )
        thread.start()
        self.log("REAL DB thread started")
        return thread

    def log(self, message: str) -> None:
        super().log(message)

    def should_stop(self):
        return super().should_stop()
