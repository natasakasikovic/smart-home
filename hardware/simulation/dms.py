import random
import time
import threading
from ..base.dms_interface import DMSInterface

DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


def loop(dms):
    dms.log("DMS simulation started")
    while not dms.should_stop():
        pin = dms.detect_press_change()

        if pin is not None:
            dms.callback(pin, dms.config)

        time.sleep(dms.config.get('poll_interval', 0.5))

    dms.log("DMS simulation loop stopped")


class DMS(DMSInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.pin_length = config.get("pin_length", 4)
        self.log(
            "Initializing DMS (Door Membrane Switch) simulated on pin {}".format(
                self.config.get('pin', 'N/A')
            )
        )

    def detect_press_change(self):
        if random.random() < 0.08:
            pin = ''.join(random.choices(DIGITS, k=self.pin_length))
            self.log(f"Simulated PIN entry: {pin}")
            return pin

        return None

    def start(self):
        thread = threading.Thread(
            target=loop,
            args=(self,),
            name=f"DMS-{self.config.get('name', 'unknown')}"
        )
        thread.daemon = True
        thread.start()
        self.log("DMS thread started")
        return thread

    def log(self, message: str) -> None:
        super().log(message)

    def should_stop(self):
        return super().should_stop()