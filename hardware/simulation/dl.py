from hardware.base.dl_interface import DLInterface

class DL(DLInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.is_on = False
        self.log("Initializing DL (Door Light) simulated on pin {}".format(self.config.get('pin', 'N/A')))

    def on(self):
        if not self.is_on:
            self.is_on = True
            self.log("Light TURNED ON (simulated)")
            self.callback(self.config, self.is_on)
        else:
            self.log("Light is already TURNED ON")

    def off(self):
        if self.is_on:
            self.is_on = False
            self.callback(self.config, self.is_on)
            self.log("Light TURNED OFF (simulated)")
        else:
            self.log("Light is already TURNED OFF")