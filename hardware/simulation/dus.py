from hardware.base.dus_interface import DUSInterface
import threading, time

def loop(dus):
    dus.log("DUS simulation started")
    while not dus.should_stop():
        distance = dus.detect()
    
        if distance is not None:
            dus.callback(distance, dus.config)
        
        time.sleep(dus.config.get('poll_interval', 0.5))

    dus.log("DUS simulation loop stopped")


class DUS(DUSInterface):
    def __init__(self, config, stop_event, callback, threshold: float = 50):
        super().__init__(config, stop_event, callback)
        self.threshold = threshold
        self.log("Initializing SIMULATED DUS (Door Ultrasonic Sensor) on pin {}".format(self.config.get('pin', 'N/A')))

    def detect(self):
        import random
        distance = random.uniform(0, self.threshold + 1000)

        if distance < self.threshold:
            self.log(f"Detected object at {distance:.1f} cm (simulated)")
       
        return distance
    
    def start(self):
        """Starts the DUS simulation in a separate thread"""
        thread = threading.Thread(
            target=loop,
            args=(self,),
            name=f"DUS-{self.config.get('name', 'unknown')}"
        )
        thread.daemon = True
        thread.start()
        self.log("DUS thread started")
        return thread