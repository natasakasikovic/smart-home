from abc import ABC, abstractmethod
from threading import Event
from typing import Callable, Optional, Dict, Any

class SSDInterface(ABC):

    def __init__(self, config: Dict[str, Any], stop_event: Event, callback: Optional[Callable] = None):
        self.config = config
        self.stop_event = stop_event
        self.callback = callback

        self.name = config.get("name", "4SD")
        self.verbose = config.get("verbose", False)

        self.log(f"{self.name} interface initialized")

    @abstractmethod
    def display_time(self, value: str) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def cleanup(self) -> None:
        pass

    def should_stop(self) -> bool:
        return self.stop_event.is_set()

    def log(self, message: str) -> None:
        if self.verbose:
            print(f"[{self.name}] {message}")
