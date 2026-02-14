from abc import abstractmethod
from hardware.base.actuator_interface import ActuatorInterface
import threading
from typing import Dict, Any, Callable


class LCDInterface:
    def __init__(self, config: Dict[str, Any], stop_event: threading.Event, callback: Callable):
        self.config = config
        self.stop_event = stop_event
        self.callback = callback
        self.columns = config.get("columns", 16)
        self.rows = config.get("rows", 2)
        self.backlight_on = True

    @abstractmethod
    def display_text(self, text: str, line: int = 0) -> None:
        """Display text on specified line"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the display"""
        pass

    @abstractmethod
    def change_backlight_state(self, state: bool):
        "Changes backlight state -> ON/OFF"
        pass

    @abstractmethod
    def set_cursor(self, col: int, row: int) -> None:
        """Set cursor position"""
        pass

    def log(self, message: str) -> None: 
        if self.config.get("verbose", False):
            print(message)

    def should_stop(self) -> bool:
        return self.stop_event.is_set() 