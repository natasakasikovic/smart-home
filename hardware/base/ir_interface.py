import threading
from typing import Callable, Dict, Any


class IRInterface:
    def __init__(self, config: Dict[str, Any], stop_event: threading.Event, callback: Callable):
        self.config = config
        self.stop_event = stop_event
        self.callback = callback

    def read_key(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def cleanup(self):
        pass

    def should_stop(self):
        return self.stop_event.is_set()

    def log(self, message: str) -> None:
        if self.config.get("verbose", False):
            print(f"[IR][{self.config.get('name', 'unknown')}] {message}")