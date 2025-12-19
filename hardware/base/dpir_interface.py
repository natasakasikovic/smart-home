from abc import ABC, abstractmethod

class DPIRInterface(ABC):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)

    @abstractmethod
    def detect_motion(self) -> bool:
        pass