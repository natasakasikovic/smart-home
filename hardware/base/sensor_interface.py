from abc import ABC, abstractmethod
from typing import Callable, Any, Dict
import threading

class SensorInterface(ABC):

  def __init__(self, config: Dict[str, Any], stop_event: threading.Event, callback: Callable):
        self.config = config
        self.stop_event = stop_event
        self.callback = callback
  
  @abstractmethod
  def start(self) -> None:
        pass
  
  def should_stop(self) -> bool:
        return self.stop_event.is_set()
  
  def log(self, message: str) -> None:
        if self.config.get("verbose", False):
            print(message)