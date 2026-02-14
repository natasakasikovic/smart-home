from hardware.base.sensor_interface import SensorInterface
from threading import Event
from typing import Callable, Tuple, Optional

class DHTInterface(SensorInterface):
    def __init__(self, config: dict, stop_event: Event, callback: Optional[Callable] = None):
        """
        Base interface for DHT sensors (temperature + humidity).
        
        :param config: sensor configuration dictionary (pin, name, poll_interval, etc.)
        :param stop_event: threading.Event to signal stopping the loop
        :param callback: optional function to call on new readings
        """
        super().__init__(config, stop_event, callback)

    def read(self) -> Tuple[float, float]:
        """
        Should return a tuple: (temperature in °C, humidity in %)
        """
        raise NotImplementedError("Subclasses must implement the read() method")