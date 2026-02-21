import time
import threading
from datetime import datetime

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from ..base.ir_interface import IRInterface

BUTTONS = [
    0x300ff22dd, 0x300ffc23d, 0x300ff629d, 0x300ffa857,
    0x300ff9867, 0x300ffb04f, 0x300ff6897, 0x300ff02fd,
    0x300ff30cf, 0x300ff18e7, 0x300ff7a85, 0x300ff10ef,
    0x300ff38c7, 0x300ff5aa5, 0x300ff42bd, 0x300ff4ab5,
    0x300ff52ad
]
BUTTON_NAMES = [
    "LEFT", "RIGHT", "UP", "DOWN", "2", "3", "1", "OK",
    "4", "5", "6", "7", "8", "9", "*", "0", "#"
]


def get_binary(pin):
    num1s = 0
    binary = 1
    command = []
    previousValue = 0
    value = GPIO.input(pin)

    while value:
        time.sleep(0.0001)
        value = GPIO.input(pin)

    startTime = datetime.now()

    while True:
        if previousValue != value:
            now = datetime.now()
            pulseTime = now - startTime
            startTime = now
            command.append((previousValue, pulseTime.microseconds))

        if value:
            num1s += 1
        else:
            num1s = 0

        if num1s > 10000:
            break

        previousValue = value
        value = GPIO.input(pin)

    for (typ, tme) in command:
        if typ == 1:
            if tme > 1000:
                binary = binary * 10 + 1
            else:
                binary *= 10

    if len(str(binary)) > 34:
        binary = int(str(binary)[:34])

    return binary


def convert_hex(binary_value):
    tmp = int(str(binary_value), 2)
    return hex(tmp)


def loop(ir):
    ir.log("REAL IR loop started")

    try:
        GPIO.setmode(GPIO.BCM)
    except ValueError:
        pass

    GPIO.setup(ir.pin, GPIO.IN)

    while not ir.should_stop():
        try:
            in_data = convert_hex(get_binary(ir.pin))
            for i, button_hex in enumerate(BUTTONS):
                if hex(button_hex) == in_data:
                    key_name = BUTTON_NAMES[i]
                    ir.log(f"Key pressed: {key_name}")
                    ir.callback(key_name, ir.config)
                    break
        except Exception as e:
            ir.log(f"Error reading IR: {e}")
            time.sleep(0.1)

    ir.cleanup()
    ir.log("REAL IR loop stopped")


class IR(IRInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.pin = self.config.get("pin", 17)
        self.log(f"Initializing REAL IR Receiver on pin {self.pin}")

    def start(self):
        thread = threading.Thread(
            target=loop,
            args=(self,),
            name=f"IR-{self.config.get('name', 'unknown')}",
            daemon=True
        )
        thread.start()
        self.log("REAL IR thread started")
        return thread

    def cleanup(self):
        self.log(f"Cleaning up GPIO pin {self.pin}")
        GPIO.cleanup(self.pin)