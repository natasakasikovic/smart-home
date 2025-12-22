import threading
from typing import Dict, Any


class DBManager:

    @staticmethod
    def create_db(
        config: Dict[str, Any],
        stop_event: threading.Event
    ):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated DB for {config.get('name', 'unknown')}.")
            from hardware.simulation.db import DB
            return DB(config, stop_event)
        else:
            print(f"Creating real DB for {config.get('name', 'unknown')}.")
            from hardware.real.db import DB
            return DB(config, stop_event)

    @staticmethod
    def start_db(
        config: Dict[str, Any],
        stop_event: threading.Event
    ):
        db = DBManager.create_db(config, stop_event)

        print(
            f"[DB_MANAGER] DB '{config.get('name', 'unknown')}' initialized successfully"
        )

        return db
