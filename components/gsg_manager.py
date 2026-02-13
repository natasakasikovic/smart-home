import threading
from typing import Callable, Dict, Any


class GSGManager:

    @staticmethod
    def create_gsg(
        config: Dict[str, Any],
        stop_event: threading.Event,
        callback: Callable
    ):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated GSG for {config.get('name', 'unknown')}.")
            from hardware.simulation.gsg import GSG
            return GSG(config, stop_event, callback)
        else:
            print(f"Creating real GSG for {config.get('name', 'unknown')}.")
            from hardware.real.gsg.gsg import GSG
            return GSG(config, stop_event, callback)

    @staticmethod
    def start_gsg(
        config: Dict[str, Any],
        stop_event: threading.Event,
        publisher=None
    ) -> threading.Thread:

        def gsg_callback(data, cfg):
            payload = {
                "name": cfg.get("name", "unknown"),
                "type": "GSG",
                "accelerometer": {
                    "x": data["accel"][0],
                    "y": data["accel"][1],
                    "z": data["accel"][2],
                    "x_g": data["accel_g"][0],
                    "y_g": data["accel_g"][1],
                    "z_g": data["accel_g"][2]
                },
                "gyroscope": {
                    "x": data["gyro"][0],
                    "y": data["gyro"][1],
                    "z": data["gyro"][2],
                    "x_dps": data["gyro_dps"][0],
                    "y_dps": data["gyro_dps"][1],
                    "z_dps": data["gyro_dps"][2]
                },
                "simulated": cfg.get("simulated", True),
                "runs_on": cfg.get("runs_on", "unknown")
            }

            topic = cfg.get("topic", "sensors/gsg")
            publisher.add_measurement(topic, payload)

        gsg = GSGManager.create_gsg(config, stop_event, gsg_callback)
        thread = gsg.start()

        print(f"[GSG_MANAGER] GSG '{config.get('name', 'unknown')}' started successfully")
        return thread