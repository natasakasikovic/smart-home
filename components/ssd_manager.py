import threading
from typing import Callable, Dict, Any


class SSDManager():

    @staticmethod
    def create_ssd(
        config: Dict[str, Any],
        stop_event: threading.Event,
        callback: Callable
    ):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated SSD for {config.get('name', 'unknown')}.")
            from hardware.simulation.ssd import SSD
            return SSD(config, stop_event, callback)
        else:
            print(f"Creating real SSD for {config.get('name', 'unknown')}.")
            from hardware.real.ssd import SSD
            return SSD(config, stop_event, callback)


    @staticmethod
    def start_ssd(
        config: Dict[str, Any],
        stop_event: threading.Event,
        publisher=None
    ):

        def segment_callback(action_data, cfg):
            payload = {
                "name": cfg.get("name", "unknown"),
                "type": "4SD",
                "action": action_data.get("action", "unknown"),
                "data": action_data,
                "simulated": cfg.get("simulated", True),
                "runs_on": cfg.get("runs_on", "unknown")
            }

            topic = cfg.get("topic", "actuators/4sd")
            
            if publisher:
                publisher.add_measurement(topic, payload)

        segment = SSDManager.create_ssd(config, stop_event, segment_callback)

        print(f"[4SD_MANAGER] 4SD '{config.get('name', 'unknown')}' started successfully")

        return segment
