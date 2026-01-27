import random
import time
import threading
from ..base.dms_interface import DMSInterface

choices = [1,2,3,4,5,6,7,8,9,10, 'A', 'B', 'C', 'D', '*', '#', '0']

def loop(dms):
    dms.log("DMS simulation started")
    while not dms.should_stop():
        press_change = dms.detect_press_change()

        if press_change is not None:
            dms.callback(press_change, dms.config)

        time.sleep(dms.config.get('poll_interval', 0.5))

    dms.log("DMS simulation loop stopped")


class DMS(DMSInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.log(
            "Initializing DMS (Door Membrane Switch) simulated on pin {}".format(
                self.config.get('pin', 'N/A')
            )
        )

    def detect_press_change(self) -> bool:
        if random.random() < 0.08:
            self.is_pressed = not getattr(self, "is_pressed", False)

            index = random.randint(0, len(choices) - 1)

            if self.is_pressed:
                self.log(f"Simulated input (door pressed): {choices[index]}")
            else:
                self.log(f"Simulated input (door released): {choices[index]}")

        return getattr(self, "is_pressed", False)

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