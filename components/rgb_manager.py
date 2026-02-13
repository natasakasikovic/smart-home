import threading
from typing import Callable, Dict, Any


class RGBManager:

    @staticmethod
    def create_rgb(
        config: Dict[str, Any],
        stop_event: threading.Event,
        callback: Callable
    ):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated RGB for {config.get('name', 'unknown')}.")
            from hardware.simulation.rgb import RGB
            return RGB(config, stop_event, callback)
        else:
            print(f"Creating real RGB for {config.get('name', 'unknown')}.")
            from hardware.real.rgb import RGB
            return RGB(config, stop_event, callback)

    @staticmethod
    def start_rgb(
        config: Dict[str, Any],
        stop_event: threading.Event,
        publisher=None
    ):
        def rgb_callback(cfg, color):
            payload = {
                "name": cfg.get("name", "unknown"),
                "type": "rgb",
                "color": color,
                "simulated": cfg.get("simulated", True),
                "runs_on": cfg.get("runs_on", "unknown")
            }

            topic = cfg.get("topic", "actuators/rgb")
            publisher.add_measurement(topic, payload)

        rgb = RGBManager.create_rgb(config, stop_event, rgb_callback)

        print(f"[RGB_MANAGER] RGB '{config.get('name', 'unknown')}' initialized successfully")

        return rgb