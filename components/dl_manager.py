import threading
from typing import Callable, Dict, Any

class DLManager():

    @staticmethod
    def create_dl(
        config: Dict[str, Any],
        stop_event: threading.Event,
        callback: Callable
    ):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated DL for {config.get('name', 'unknown')}.")
            from hardware.simulation.dl import DL
            return DL(config, stop_event, callback)
        else:
            print(f"Creating real DL for {config.get('name', 'unknown')}.")
            from hardware.real.dl import DL
            return DL(config, stop_event, callback)

    @staticmethod
    def start_dl(
        config: Dict[str, Any],
        stop_event: threading.Event,
        publisher = None
    ):
        def dl_callback(cfg, is_on):
            payload = {
                "name": cfg.get("name", "unknown"),
                "type": "dl",
                "turned_on": is_on,
                "simulated": cfg.get("simulated", True),
                "runs_on": cfg.get("runs_on", "unknown")
            }

            topic = cfg.get("topic", "actuators/dl")
            publisher.add_measurement(topic, payload)

        dl = DLManager.create_dl(config, stop_event, dl_callback)

        print(
            f"[DL_MANAGER] DL '{config.get('name', 'unknown')}' initialized successfully"
        )

        return dl