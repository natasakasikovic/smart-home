import time
import random
import threading

from ..base.ir_interface import IRInterface

SIMULATED_KEYS = ["LEFT", "RIGHT", "UP", "DOWN", "OK", "1", "2", "3", "0", "#", "*"]


def loop(ir):
    ir.log("IR simulation started")
    while not ir.should_stop():
        time.sleep(random.uniform(2, 5))
        if ir.should_stop():
            break
        key = random.choice(SIMULATED_KEYS)
        ir.log(f"Key pressed (simulated): {key}")
        ir.callback(key, ir.config)

    ir.log("IR simulation loop stopped")


class IR(IRInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.log("Initializing SIMULATED IR Receiver")

    def start(self):
        thread = threading.Thread(
            target=loop,
            args=(self,),
            name=f"IR-{self.config.get('name', 'unknown')}",
            daemon=True
        )
        thread.start()
        self.log("IR simulation thread started")
        return thread