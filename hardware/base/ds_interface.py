from abc import abstractmethod
from hardware.base.sensor_interface import SensorInterface

class DSInterface(SensorInterface):

    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.is_open = False

    @abstractmethod
    def detect_state_change(self) -> bool:
        pass
