import threading
from typing import Callable, Dict, Any


class DBManager:

    @staticmethod
    def create_db(
        config: Dict[str, Any],
        stop_event: threading.Event,
        callback: Callable
    ):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated DB for {config.get('name', 'unknown')}.")
            from hardware.simulation.db import DB
            return DB(config, stop_event, callback)
        else:
            print(f"Creating real DB for {config.get('name', 'unknown')}.")
            from hardware.real.db import DB
            return DB(config, stop_event, callback)

    @staticmethod
    def start_db(
        config: Dict[str, Any],
        stop_event: threading.Event,
        publisher=None
    ):
        def db_callback(cfg):
            payload = {
                "name": cfg.get("name", "unknown"),
                "type": "db",
                "buzzing": True,
                "simulated": cfg.get("simulated", True),
                "runs_on": cfg.get("runs_on", "unknown")
            }

            topic = cfg.get("topic", "sensors/db")
            publisher.add_measurement(topic, payload)

        db = DBManager.create_db(config, stop_event, db_callback)

        print(f"[DB_MANAGER] DB '{config.get('name', 'unknown')}' initialized successfully")

        return db
