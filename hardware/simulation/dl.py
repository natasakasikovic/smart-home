from hardware.base.dl_interface import DLInterface

class DL(DLInterface):
    def __init__(self, config, stop_event):
        super().__init__(config, stop_event)
        self.is_on = False
        self.log("Initializing DL (Door Light) simulated on pin {}".format(self.config.get('pin', 'N/A')))

    def on(self):
        if not self.is_on:
            self.is_on = True
            self.log("Light TURNED ON (simulated)")

    def off(self):
        if self.is_on:
            self.is_on = False
            self.log("Light TURNED OFF (simulated)")