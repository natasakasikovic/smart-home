from hardware.base.sensor_interface import SensorInterface
from abc import abstractmethod 

class DUSInterface(SensorInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)

    @abstractmethod
    def detect(self):
        """Returns the distance to the nearest object in cm"""
        pass