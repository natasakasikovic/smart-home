import random
import time
import threading
from ..base.ds_interface import DSInterface


def loop(ds):
    ds.log("DS simulation started")
    while not ds.should_stop():
        state_change = ds.detect_state_change()

        if state_change is not None:
            ds.callback(state_change, ds.config)

        time.sleep(ds.config.get('poll_interval', 0.5))

    ds.log("DS simulation loop stopped")


class DS(DSInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.log(
            "Initializing DS (Door Sensor) simulated via button on pin {}".format(
                self.config.get('pin', 'N/A')
            )
        )

    def detect_state_change(self) -> bool:
        """
        Simulates door open/close events.
        Internally uses a button-like mechanism.
        """
        if random.random() < 0.1:
            self.is_open = not getattr(self, "is_open", False)

            if self.is_open:
                self.log("DOOR OPENED (simulated)")
            else:
                self.log("DOOR CLOSED (simulated)")

        return getattr(self, "is_open", False)


    def start(self):
        """Starts the DS simulation in a separate thread"""
        thread = threading.Thread(
            target=loop,
            args=(self,),
            name=f"DS-{self.config.get('name', 'unknown')}"
        )
        thread.daemon = True
        thread.start()
        self.log("DS thread started")
        return thread

    def log(self, message: str) -> None:
        super().log(message)

    def should_stop(self):
        return super().should_stop()
