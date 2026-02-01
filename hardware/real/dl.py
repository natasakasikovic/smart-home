from hardware.base.dl_interface import DLInterface

class DL(DLInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.log("Initializing REAL DL (Door Light) on pin {}".format(self.config.get('pin', 'N/A')))