from abc import abstractmethod
from .actuator_interface import ActuatorInterface


class RGBInterface(ActuatorInterface):

    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)

    @abstractmethod
    def off(self) -> None:
        """Turn RGB LED OFF"""
        pass

    @abstractmethod
    def set_color(self, red: bool, green: bool, blue: bool) -> None:
        """Set RGB color by controlling individual channels"""
        pass

    @abstractmethod
    def white(self) -> None:
        """Set color to white"""
        pass

    @abstractmethod
    def red(self) -> None:
        """Set color to red"""
        pass

    @abstractmethod
    def green(self) -> None:
        """Set color to green"""
        pass

    @abstractmethod
    def blue(self) -> None:
        """Set color to blue"""
        pass

    @abstractmethod
    def yellow(self) -> None:
        """Set color to yellow"""
        pass

    @abstractmethod
    def purple(self) -> None:
        """Set color to purple"""
        pass

    @abstractmethod
    def light_blue(self) -> None:
        """Set color to light blue (cyan)"""
        pass