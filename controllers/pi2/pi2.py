import threading
import signal

from publisher import Publisher
from utils.config_loader import load_config


def start_sensors(config, stop_event, publisher):
    # TODO: add sensors
    return []


def start_actuators(config, stop_event, publisher):
    # TODO: add actuators
    return {}


def run():
    print("[PI2] Starting...")

    config = load_config("config/settings.json")
    pi_config = config["PI2"]

    stop_event = threading.Event()

    signal.signal(signal.SIGINT, lambda s, f: stop_event.set())
    signal.signal(signal.SIGTERM, lambda s, f: stop_event.set())

    publisher = Publisher(config["mqtt"])
    publisher.start_daemon()

    threads = start_sensors(pi_config, stop_event, publisher)
    actuators = start_actuators(pi_config, stop_event, publisher)

    print("[PI2] System ready.")

    try:
        while not stop_event.is_set():
            # TODO: add command handler
            stop_event.wait(0.5)

    except KeyboardInterrupt:
        stop_event.set()
        publisher.stop_event.set()

    finally:
        print("[PI2] Stopping publisher...")
        publisher.shutdown()

        print("[PI2] Waiting for threads to finish...")
        for t in threads:
            if t.is_alive():
                t.join(timeout=2)

        print("[PI2] Shutdown complete")
