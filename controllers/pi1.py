import json
import threading
import sys
import signal
from components.ds_manager import DSManager
from components.dpir_manager import DPIRManager
from components.db_manager import DBManager

# NOTE: this function should be moved to a common utility module
def load_config(config_path: str = "settings.json") -> dict:
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get("PI1", {})
    except Exception as e:
        print(f"[ERROR] Failed to load config: {e}")
        sys.exit(1)

def start_sensors(config, stop_event, publisher=None):
    threads = []

    if "DS1" in config:
        ds1_config = config["DS1"]
        ds1_config['code'] = 'DS1'
        thread = DSManager.start_ds(ds1_config, stop_event, publisher)
        threads.append(thread)

    if "DPIR1" in config:
        dpir1_config = config["DPIR1"]
        dpir1_config['code'] = 'DPIR1'
        thread = DPIRManager.start_dpir(dpir1_config, stop_event, publisher)
        threads.append(thread)

    # TODO: add other sensors when implemented
    return threads


def start_actuators(config, stop_event):
    actuators = {}

    if "DB" in config:
        db_config = config["DB"]
        db_config["code"] = "DB"
        db = DBManager.start_db(db_config, stop_event)
        actuators["DB"] = db

    # TODO: add other actuators
    return actuators


def run():
    print("[PI1] Starting...")
    config = load_config("config/settings.json")
    stop_event = threading.Event()

    signal.signal(signal.SIGINT, lambda s, f: stop_event.set())
    signal.signal(signal.SIGTERM, lambda s, f: stop_event.set())

    threads = start_sensors(config, stop_event)
    actuators = start_actuators(config, stop_event)

    try:
        while not stop_event.is_set():
            command = input(">>> ").strip().lower()
            if command in ("e", "exit", "quit"):
                print("[PI1] Shutting down...")
                stop_event.set()
            elif command == "status":
                print(f"[PI1] Active threads: {len([t for t in threads if t.is_alive()])}")
            
            # TODO: EXTRACT
            elif command == "db on":
                actuators["DB"].on()

            elif command == "db off":
                actuators["DB"].off()

            elif command.startswith("db beep"):
                try:
                    _, _, duration = command.split()
                    actuators["DB"].beep(float(duration))
                except Exception:
                    print("Usage: db beep <seconds>")


            else:
                print("[PI1] Unknown command")
    except KeyboardInterrupt:
        stop_event.set()

    for t in threads:
        if t.is_alive():
            t.join()
    print("[PI1] Shutdown complete")
