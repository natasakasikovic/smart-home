from abc import abstractmethod
from hardware.base.sensor_interface import SensorInterface

class DPIRInterface(SensorInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)

    @abstractmethod
    def detect_motion(self) -> bool:
        pass