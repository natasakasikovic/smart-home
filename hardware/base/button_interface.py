from abc import abstractmethod
from hardware.base.sensor_interface import SensorInterface

class ButtonInterface(SensorInterface):

    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.pressed = False

    @abstractmethod
    def detect_press(self) -> bool:
        pass
