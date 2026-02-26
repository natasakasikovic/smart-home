import threading
from typing import Callable, Dict, Any


class IRManager:

    @staticmethod
    def create_ir(
        config: Dict[str, Any],
        stop_event: threading.Event,
        callback: Callable
    ):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated IR for {config.get('name', 'unknown')}.")
            from hardware.simulation.ir import IR
            return IR(config, stop_event, callback)
        else:
            print(f"Creating real IR for {config.get('name', 'unknown')}.")
            from hardware.real.ir import IR
            return IR(config, stop_event, callback)

    @staticmethod
    def start_ir(
        config: Dict[str, Any],
        stop_event: threading.Event,
        publisher=None
    ) -> threading.Thread:

        def ir_callback(key_name, cfg):
            payload = {
                "name": cfg.get("name", "unknown"),
                "type": "IR",
                "key": key_name,
                "simulated": cfg.get("simulated", True),
                "runs_on": cfg.get("runs_on", "unknown")
            }

            topic = cfg.get("topic", "sensors/ir1")
            publisher.add_measurement(topic, payload)

        ir = IRManager.create_ir(config, stop_event, ir_callback)
        thread = ir.start()

        print(f"[IR_MANAGER] IR '{config.get('name', 'unknown')}' started successfully")
        return thread