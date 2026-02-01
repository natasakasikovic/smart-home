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
                "state": "PRESSED" if state else "RELEASED",
                "simulated": cfg.get("simulated", True)
            }

            topic = cfg.get("topic", "sensors/dns")
            publisher.add_measurement(topic, payload)

        dms = DMSManager.create_dms(config, stop_event, dms_callback)
        thread = dms.start()

        print(f"[DMS_MANAGER] DMS '{config.get('name', 'unknown')}' started successfully")
        return thread