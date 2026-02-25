import threading
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from hardware.base.btn_interface import BTNInterface


def loop(btn):
    try:
        while not btn.should_stop():
            try:
                command = btn.pipe.recv()
            except EOFError:
                break
            except Exception as e:
                btn.log(f"Pipe error: {e}")
                break

            if command == "l":
                if btn.is_on:
                    btn.off()
                else:
                    btn.on()

            state = btn.get_state()

            if btn.callback:
                btn.callback(state, btn.config)

            time.sleep(0.01) 

    finally:
        btn.clean_up()


class BTN(BTNInterface):
    def __init__(self, config, stop_event, callback=None, pipe=None):
        super().__init__(config, stop_event, callback)

        if GPIO is None:
            raise RuntimeError("RPi.GPIO not available on this system")

        self.callback = callback
        self.pipe = pipe

        self.pin = config["pin"]
        self.is_on = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)

        self.callback(self.config, self.is_on)
        self.log("Initializing REAL BTN (Kitchen Button) on pin {}".format(self.config.get('pin', 'N/A')))

    def on(self):
        if not self.is_on:
            self.is_on = True
            GPIO.output(self.pin, GPIO.HIGH)
            self.log("Kitchen Button PRESSED")

    def off(self):
        if self.is_on:
            self.is_on = False
            GPIO.output(self.pin, GPIO.LOW)
            self.log("Kitchen Button RELEASED")

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