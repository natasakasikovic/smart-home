from abc import abstractmethod
from .actuator_interface import ActuatorInterface


class DBInterface(ActuatorInterface):

    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)

    @abstractmethod
    def on(self) -> None:
        """Turn buzzer ON"""
        pass

    @abstractmethod
    def off(self) -> None:
        """Turn buzzer OFF"""
        pass

    @abstractmethod
    def beep(self, duration: float) -> None:
        """Make the buzzer beep for a specified duration in seconds"""
        pass