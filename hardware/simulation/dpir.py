from ..base.dpir_interface import DPIRInterface

def loop(dpir):
    dpir.log("Simulation DPIR started")
    while not dpir.should_stop():
        pass

class DPIR(DPIRInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.log("Initializing simulated DPIR on pin {}".format(self.config.get('pin', 'N/A')))

    def detect_motion(self) -> bool:
        """Motion detection is simulated using random values to emulate real sensor behavior."""
        import random
        value = random.randint(0,1) == 1
        if value:
            self.log('Motion DETECTED')
        return value
    
    def start(self):
        """Starts the simulation in a separate thread"""
        import threading
        thread = threading.Thread(
            target=loop, 
            args=(self,),
            name=f"SimDPIR-{self.config.get('name', 'unknown')}"
        )
        thread.daemon = True
        thread.start()
        self.log("Thread started")
        return thread

    def should_stop(self):
        return super().should_stop()