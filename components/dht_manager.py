import threading
from typing import Callable, Dict, Any

class DHTManager:

    @staticmethod
    def create_dht(config: Dict[str, Any], stop_event: threading.Event, callback: Callable):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated DHT for {config.get('name', 'unknown')}.")
            from hardware.simulation.dht import DHT
            return DHT(config, stop_event, callback)
        else:
            print(f"Creating real DHT for {config.get('name', 'unknown')}.")
            from hardware.real.dht.dht import DHT
            return DHT(config, stop_event, callback)

    @staticmethod
    def start_dht(config: Dict[str, Any], stop_event: threading.Event, publisher=None) -> threading.Thread:

        def dht_callback(data):
            payload = {
                "name": config.get("name", "unknown"),
                "type": "dht",
                "code": config.get("code"),
                "temperature": data.get("temperature"),
                "humidity": data.get("humidity"),
                "simulated": config.get("simulated", True),
                "runs_on": config.get("runs_on", "unknown")
            }

            topic = config.get("topic", "sensors/dht1")

            if publisher:
                publisher.add_measurement(topic, payload)
            else:
                print("[DHT_MANAGER] No publisher defined. Payload:", payload)

        dht = DHTManager.create_dht(config, stop_event, dht_callback)
        thread = dht.start()

        print(f"[DHT_MANAGER] DHT '{config.get('name', 'unknown')}' started successfully")
        return thread