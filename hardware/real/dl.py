from hardware.base.dl_interface import DLInterface

class DL(DLInterface):
    def __init__(self, config, stop_event):
        super().__init__(config, stop_event)
        self.log("Initializing REAL DL (Door Light) on pin {}".format(self.config.get('pin', 'N/A')))