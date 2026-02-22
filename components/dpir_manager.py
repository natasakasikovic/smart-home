import threading
from typing import Callable, Dict, Any

class DPIRManager():
    
    def create_dpir(config: Dict[str, Any], stop_event: threading.Event, callback: Callable):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated dpir for {config.get('name', 'unknown')}.")
            from hardware.simulation.dpir import DPIR
            return DPIR(config, stop_event, callback)
        else:
            print(f"Creating real dpir for {config.get('name', 'unknown')}.")
            from hardware.real.dpir import DPIR
            return DPIR(config, stop_event, callback)
        
    @staticmethod
    def start_dpir(config: Dict[str, Any], stop_event: threading.Event, publisher=None) -> threading.Thread:
        def dpir_callback(cfg):
            payload = {
                "name": cfg.get("name", "unknown"),
                "type": "dpir",
                "detected": True,
                "simulated": cfg.get("simulated", True),
                "runs_on": cfg.get("runs_on", "unknown")
            }
            
            topic = cfg.get("topic", "sensors/dpir")
            publisher.add_measurement(topic, payload)

        dpir = DPIRManager.create_dpir(config, stop_event, dpir_callback)
        thread = dpir.start()

        print(f"[DPIR_MANAGER] DPIR '{config.get('name', 'unknown')}' started successfully")
        return thread