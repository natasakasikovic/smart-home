import threading
from typing import Callable, Dict, Any


class DMSManager:

    @staticmethod
    def create_dms(
        config: Dict[str, Any],
        stop_event: threading.Event,
        callback: Callable
    ):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated DMS for {config.get('name', 'unknown')}.")
            from hardware.simulation.dms import DMS
            return DMS(config, stop_event, callback)
        else:
            print(f"Creating real DMS for {config.get('name', 'unknown')}.")
            from hardware.real.dms import DMS
            return DMS(config, stop_event, callback)

    @staticmethod
    def start_dms(
        config: Dict[str, Any],
        stop_event: threading.Event,
        publisher=None
    ) -> threading.Thread:

        def dms_callback(state, cfg):
            payload = {
                "name": cfg.get("name", "unknown"),
                "type": "DMS",
                "pin": str(state) if state else "",
                "simulated": cfg.get("simulated", True),
                "runs_on": cfg.get("runs_on", "unknown")
            }

            topic = cfg.get("topic", "actuators/dms")
            publisher.add_measurement(topic, payload)

        dms = DMSManager.create_dms(config, stop_event, dms_callback)
        thread = dms.start()

        print(f"[DMS_MANAGER] DMS '{config.get('name', 'unknown')}' started successfully")
        return thread