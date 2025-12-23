from hardware.base.dus_interface import DUSInterface

def loop(dus):
    pass

class DUS(DUSInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.log("Initializing REAL DUS (Door Ultrasonic Sensor) on pin {}".format(self.config.get('pin', 'N/A')))

    def detect(self):
        print("Real DUS not implemented yet")
        pass