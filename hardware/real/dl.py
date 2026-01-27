import threading
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from hardware.base.dl_interface import DLInterface


def loop(light):
    try:
        while not light.should_stop():
            try:
                command = light.pipe.recv()
            except EOFError:
                break
            except Exception as e:
                light.log(f"Pipe error: {e}")
                break

            if command == "l":
                if light.is_on:
                    light.off()
                else:
                    light.on()

            state = light.get_state()

            if light.callback:
                light.callback(state, light.config)

            time.sleep(0.01) 

    finally:
        light.clean_up()


class DL(DLInterface):
    def __init__(self, config, stop_event, callback=None, pipe=None):
        super().__init__(config, stop_event)

        if GPIO is None:
            raise RuntimeError("RPi.GPIO not available on this system")

        self.callback = callback
        self.pipe = pipe

        self.pin = config["pin"]
        self.is_on = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)

        self.log("Initializing REAL DL (Door Light) on pin {}".format(self.config.get('pin', 'N/A')))

    def on(self):
        if not self.is_on:
            self.is_on = True
            GPIO.output(self.pin, GPIO.HIGH)
            self.log("Light TURNED ON")

    def off(self):
        if self.is_on:
            self.is_on = False
            GPIO.output(self.pin, GPIO.LOW)
            self.log("Light TURNED OFF")

    def get_state(self):
        return "on" if self.is_on else "off"

    def should_stop(self):
        return self.stop_event.is_set()

    def start(self):
        t = threading.Thread(target=loop, args=(self,), daemon=True)
        t.start()
        return t

    def clean_up(self):
        GPIO.output(self.pin, GPIO.LOW)
        GPIO.cleanup(self.pin)
        self.log("GPIO cleaned up")