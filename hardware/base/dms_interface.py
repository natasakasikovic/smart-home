from abc import abstractmethod
from hardware.base.sensor_interface import SensorInterface

class DMSInterface(SensorInterface):

    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.is_pressed = False

    @abstractmethod
    def detect_press_change(self) -> bool:
        pass