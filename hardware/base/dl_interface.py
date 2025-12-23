from hardware.base.actuator_interface import ActuatorInterface
from abc import abstractmethod

class DLInterface(ActuatorInterface):
    def __init__(self, config, stop_event):
        super().__init__(config, stop_event)