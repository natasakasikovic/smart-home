import threading
from typing import Callable, Dict, Any

class BTNManager():

    @staticmethod
    def create_btn(
        config: Dict[str, Any],
        stop_event: threading.Event,
        callback: Callable
    ):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated BTN for {config.get('name', 'unknown')}.")
            from hardware.simulation.btn import BTN
            return BTN(config, stop_event, callback)
        else:
            print(f"Creating real BTN for {config.get('name', 'unknown')}.")
            from hardware.real.btn import BTN
            return BTN(config, stop_event, callback)

    @staticmethod
    def start_btn(
        config: Dict[str, Any],
        stop_event: threading.Event,
        publisher = None
    ):
        def btn_callback(cfg, is_on):
            payload = {
                "name": cfg.get("name", "unknown"),
                "type": "btn",
                "turned_on": is_on,
                "simulated": cfg.get("simulated", True),
                "runs_on": cfg.get("runs_on", "unknown")
            }

            topic = cfg.get("topic", "actuators/btn")
            publisher.add_measurement(topic, payload)

        btn = BTNManager.create_btn(config, stop_event, btn_callback)

        print(
            f"[BTN_MANAGER] BTN '{config.get('name', 'unknown')}' initialized successfully"
        )

        return btn