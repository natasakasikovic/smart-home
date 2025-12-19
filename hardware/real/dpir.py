from ..base.dpir_interface import DPIRInterface

def loop(dpir):
    pass

class DPIR(DPIRInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.log("Initializing real DPIR on pin {}".format(self.config.get('pin', 'N/A')))

    def detect_motion(self) -> bool:
        pass

    def should_stop(self):
        pass
