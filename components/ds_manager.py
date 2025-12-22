import threading
from typing import Callable, Dict, Any


class DSManager:

    @staticmethod
    def create_ds(
        config: Dict[str, Any],
        stop_event: threading.Event,
        callback: Callable
    ):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated DS for {config.get('name', 'unknown')}.")
            from hardware.simulation.ds import DS
            return DS(config, stop_event, callback)
        else:
            print(f"Creating real DS for {config.get('name', 'unknown')}.")
            from hardware.real.ds import DS
            return DS(config, stop_event, callback)

    @staticmethod
    def start_ds(
        config: Dict[str, Any],
        stop_event: threading.Event,
        publisher=None
    ) -> threading.Thread:

        def ds_callback(state, cfg):
            payload = {
                "name": cfg.get("name", "unknown"),
                "type": "DS",
                "state": "OPEN" if state else "CLOSED"
            }

            if publisher:  # TODO: implement publisher
                publisher.add_measurement("DS", payload)

        ds = DSManager.create_ds(config, stop_event, ds_callback)
        thread = ds.start()

        print(f"[DS_MANAGER] DS '{config.get('name', 'unknown')}' started successfully")
        return thread
