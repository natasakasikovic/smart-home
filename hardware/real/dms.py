import time
import threading

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from ..base.dms_interface import DMSInterface

KEYPAD = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]


def loop(dms):
    dms.log("Real DMS loop started")
    while not dms.should_stop():
        key = dms.detect_press_change()
        if key is not None:
            if key == "#":
                if dms.pin_buffer:
                    dms.log(f"PIN entered, length: {len(dms.pin_buffer)}")
                    dms.callback(dms.pin_buffer, dms.config)
                    dms.pin_buffer = ""
            elif key == "*":
                dms.pin_buffer = ""
                dms.log("PIN cleared")
            else:
                dms.pin_buffer += key
                dms.log(f"PIN buffer: {'*' * len(dms.pin_buffer)}")

                if len(dms.pin_buffer) >= dms.pin_length:
                    dms.log(f"PIN entered, length: {len(dms.pin_buffer)}")
                    dms.callback(dms.pin_buffer, dms.config)
                    dms.pin_buffer = ""

        time.sleep(0.1)
    dms.log("Real DMS loop stopped")


class DMS(DMSInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)

        self.rows = config["rows"]   # [25, 8, 7, 1]
        self.cols = config["cols"]   # [12, 16, 20, 21]
        self.pin_buffer = ""
        self.pin_length = config.get("pin_length", 4)

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        for r in self.rows:
            GPIO.setup(r, GPIO.OUT)
            GPIO.output(r, GPIO.LOW)

        for c in self.cols:
            GPIO.setup(c, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.log("Initializing REAL DMS (Door Membrane Switch)")

    def detect_press_change(self):
        for row_idx, row_pin in enumerate(self.rows):
            GPIO.output(row_pin, GPIO.HIGH)

            for col_idx, col_pin in enumerate(self.cols):
                if GPIO.input(col_pin) == 1:
                    key = KEYPAD[row_idx][col_idx]
                    self.log(f"Key pressed: {key}")
                    GPIO.output(row_pin, GPIO.LOW)
                    time.sleep(0.3)  # debounce
                    return key

            GPIO.output(row_pin, GPIO.LOW)

        return None

    def start(self):
        thread = threading.Thread(
            target=loop,
            args=(self,),
            name="DMS-real"
        )
        thread.daemon = True
        thread.start()
        self.log("Real DMS thread started")
        return thread

    def cleanup(self):
        GPIO.cleanup()

    def log(self, message: str) -> None:
        super().log(message)

    def should_stop(self):
        return super().should_stop()