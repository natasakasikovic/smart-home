import threading
from typing import Dict, Any

class DLManager():

    @staticmethod
    def create_dl(
        config: Dict[str, Any],
        stop_event: threading.Event
    ):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated DL for {config.get('name', 'unknown')}.")
            from hardware.simulation.dl import DL
            return DL(config, stop_event)
        else:
            print(f"Creating real DL for {config.get('name', 'unknown')}.")
            from hardware.real.dl import DL
            return DL(config, stop_event)

    @staticmethod
    def start_dl(
        config: Dict[str, Any],
        stop_event: threading.Event
    ):
        dl = DLManager.create_dl(config, stop_event)

        print(
            f"[DL_MANAGER] DL '{config.get('name', 'unknown')}' initialized successfully"
        )

        return dl