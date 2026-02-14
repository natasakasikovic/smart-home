from ..base.rgb_interface import RGBInterface


class RGB(RGBInterface):

    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.current_color = "off"
        self.log(
            "Initializing RGB LED on pins R:{}, G:{}, B:{}".format(
                self.config.get("pin_red", "N/A"),
                self.config.get("pin_green", "N/A"),
                self.config.get("pin_blue", "N/A")
            )
        )

    def set_color(self, red: bool, green: bool, blue: bool):
        color_name = self._get_color_name(red, green, blue)
        self.current_color = color_name
        self.log(f"RGB LED set to {color_name} 💡 (simulated)")
        self.callback(self.config, self.current_color)

    def on():
        pass

    def off():
        pass

    def turn_off(self):
        self.current_color = "off"
        self.log("RGB LED OFF 🌑 (simulated)")
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