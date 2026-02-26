import time
import random
from ..base.dht_interface import DHTInterface

def loop(dht):
    dht.log("Simulation DHT started")
    while not dht.should_stop():
        temp, humidity = dht.read()
        if dht.callback is not None:
            dht.callback({
                "temperature": temp,
                "humidity": humidity,
                "sensor_name": dht.config.get('name', 'unknown')
            })
        time.sleep(dht.config.get('poll_interval', 4.0)) 

    dht.log("Simulation DHT loop stopped")

class DHT(DHTInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.log("Initializing simulated DHT on pin {}".format(self.config.get('pin', 'N/A')))

    def read(self):
        """ Simulate temperature and humidity readings. """
        temp = round(random.uniform(18.0, 30.0), 1) #  18°C to 30°C
        humidity = round(random.uniform(30.0, 80.0), 1) # 30% to 80%
        self.log(f"Simulated DHT reading - Temperature: {temp}°C, Humidity: {humidity}%")
        return temp, humidity

    def start(self):
        """Starts the DHT simulation in a separate thread"""
        import threading
        thread = threading.Thread(
            target=loop, 
            args=(self,),
            name=f"SimDHT-{self.config.get('name', 'unknown')}"
        )
        thread.daemon = True
        thread.start()
        self.log("Thread started")
        return thread

    def should_stop(self):
        return super().should_stop()

    def log(self, message: str) -> None:
        super().log(message)