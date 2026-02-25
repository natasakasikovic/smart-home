from hardware.base.btn_interface import BTNInterface

class BTN(BTNInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.is_on = False
        self.callback(self.config, self.is_on)
        self.log("Initializing BTN (Kitchen Button) simulated on pin {}".format(self.config.get('pin', 'N/A')))

    def on(self):
        if not self.is_on:
            self.is_on = True
            self.log("Kitchen Button PRESSED (simulated)")
            self.callback(self.config, self.is_on)
        else:
            self.log("Kitchen Button is already PRESSED")

    def off(self):
        if self.is_on:
            self.is_on = False
            self.callback(self.config, self.is_on)
            self.log("Kitchen Button RELEASED (simulated)")
        else:
            self.log("Kitchen Button is already RELEASED")