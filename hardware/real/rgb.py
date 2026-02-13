try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from ..base.rgb_interface import RGBInterface


class RGB(RGBInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)

        self.pin_red = self.config.get("red_pin")
        self.pin_green = self.config.get("green_pin")
        self.pin_blue = self.config.get("blue_pin")
        self.current_color = "off"

        if GPIO is None:
            raise RuntimeError("RPi.GPIO nije dostupan. Pokreni na Raspberry Pi.")

        if self.pin_red is None or self.pin_green is None or self.pin_blue is None:
            raise ValueError("RGB config mora imati 'pin_red', 'pin_green', i 'pin_blue'!")

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_red, GPIO.OUT)
        GPIO.setup(self.pin_green, GPIO.OUT)
        GPIO.setup(self.pin_blue, GPIO.OUT)

        # Initialize all pins to LOW
        GPIO.output(self.pin_red, GPIO.LOW)
        GPIO.output(self.pin_green, GPIO.LOW)
        GPIO.output(self.pin_blue, GPIO.LOW)

        self.log(f"Initializing REAL RGB LED on pins R:{self.pin_red}, G:{self.pin_green}, B:{self.pin_blue}")

    def set_color(self, red: bool, green: bool, blue: bool):
        GPIO.output(self.pin_red, GPIO.HIGH if red else GPIO.LOW)
        GPIO.output(self.pin_green, GPIO.HIGH if green else GPIO.LOW)
        GPIO.output(self.pin_blue, GPIO.HIGH if blue else GPIO.LOW)

        color_name = self._get_color_name(red, green, blue)
        self.current_color = color_name
        self.log(f"RGB LED set to {color_name} 💡 (real)")
        self.callback(self.config, self.current_color)

    def turn_off(self):
        GPIO.output(self.pin_red, GPIO.LOW)
        GPIO.output(self.pin_green, GPIO.LOW)
        GPIO.output(self.pin_blue, GPIO.LOW)

        self.current_color = "off"
        self.log("RGB LED OFF 🌑 (real)")
        self.callback(self.config, self.current_color)

    def white(self):
        self.set_color(True, True, True)

    def red(self):
        self.set_color(True, False, False)

    def green(self):
        self.set_color(False, True, False)

    def blue(self):
        self.set_color(False, False, True)

    def yellow(self):
        self.set_color(True, True, False)

    def purple(self):
        self.set_color(True, False, True)

    def light_blue(self):
        self.set_color(False, True, True)

    def on():
        pass

    def off():
        pass

    def _get_color_name(self, r: bool, g: bool, b: bool) -> str:
        """Helper method to get color name from RGB values"""
        if not r and not g and not b:
            return "off"
        elif r and g and b:
            return "white"
        elif r and not g and not b:
            return "red"
        elif not r and g and not b:
            return "green"
        elif not r and not g and b:
            return "blue"
        elif r and g and not b:
            return "yellow"
        elif r and not g and b:
            return "purple"
        elif not r and g and b:
            return "light_blue"
        else:
            return "custom"

    def cleanup(self):
        GPIO.output(self.pin_red, GPIO.LOW)
        GPIO.output(self.pin_green, GPIO.LOW)
        GPIO.output(self.pin_blue, GPIO.LOW)
        GPIO.cleanup([self.pin_red, self.pin_green, self.pin_blue])
        self.log("Real RGB GPIO cleaned up")