from abc import ABC, abstractmethod
from typing import Dict, Any
import threading


class ActuatorInterface(ABC):

    def __init__(self, config: Dict[str, Any], stop_event: threading.Event):
        self.config = config
        self.stop_event = stop_event

    @abstractmethod
    def on(self) -> None:
        pass

    @abstractmethod
    def off(self) -> None:
        pass

    def log(self, message: str) -> None:
        if self.config.get("verbose", False):
            print(message)
