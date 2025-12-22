import time
import threading
from ..base.ds_interface import DSInterface


def loop(ds):
    pass


class DS(DSInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.log(
            "Initializing REAL DS (Door Sensor) on pin {}".format(
                self.config.get('pin', 'N/A')
            )
        )

    def detect_state_change(self) -> bool:
        print("Real DS state detection not implemented yet")
        return False

    def start(self):
        print("Real DS start not implemented yet")
        pass

    def cleanup(self):
        print("Real DS cleanup not implemented yet")
        pass

    def log(self, message: str) -> None:
        super().log(message)

    def should_stop(self):
        return super().should_stop()
