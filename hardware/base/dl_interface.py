from hardware.base.actuator_interface import ActuatorInterface

class DLInterface(ActuatorInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)