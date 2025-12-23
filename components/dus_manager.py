from typing import Callable, Dict, Any
import threading

class DUSManager():

    @staticmethod
    def create_dus(
        config: Dict[str, Any],
        stop_event: threading.Event,
        callback: Callable
    ):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated DUS for {config.get('name', 'unknown')}.")
            from hardware.simulation.dus import DUS
            return DUS(config, stop_event, callback)
        else: 
            print(f"Creating real DUS for {config.get('name', 'unknown')}.")
            from hardware.real.dus import DUS
            return DUS(config, stop_event, callback)


    @staticmethod
    def start_dus (config: Dict[str, Any],
        stop_event: threading.Event,
        publisher=None
    ) -> threading.Thread:
        
        def dus_callback(distance, cfg):
            payload = {
                "name": cfg.get("name", "unknown"),
                "type": "DUS",
                "distance_cm": distance
            }

            if publisher:  # TODO: implement publisher
                publisher.add_measurement("DUS", payload)

        dus = DUSManager.create_dus(config, stop_event, dus_callback)
        thread = dus.start()

        print(f"[DUS_MANAGER] DUS '{config.get('name', 'unknown')}' started successfully")
        return thread