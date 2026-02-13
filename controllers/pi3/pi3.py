import threading
import signal

from publisher import Publisher
from utils.config_loader import load_config
from components.dpir_manager import DPIRManager
from components.rgb_manager import RGBManager
from controllers.pi3.command_handler import CommandHandler

def start_sensors(config, stop_event, publisher):
    threads = []
    
    if "DPIR3" in config:
        dpir1_config = config["DPIR3"]
        dpir1_config["code"] = "DPIR3"
        threads.append(
            DPIRManager.start_dpir(dpir1_config, stop_event, publisher)
        )
    
    return threads

def start_actuators(config, stop_event, publisher):
    actuators = {}
    if "RGB" in config:
        rgb_config = config["RGB"]
        rgb_config["code"] = "RGB"
        rgb = RGBManager.start_rgb(rgb_config, stop_event, publisher)
        actuators["RGB"] = rgb
    return actuators


def run():
    print("[PI3] Starting...")

    config = load_config("config/settings.json")
    pi_config = config["PI3"]

    stop_event = threading.Event()

    signal.signal(signal.SIGINT, lambda s, f: stop_event.set())
    signal.signal(signal.SIGTERM, lambda s, f: stop_event.set())

    publisher = Publisher(config["mqtt"])
    publisher.start_daemon()

    threads = start_sensors(pi_config, stop_event, publisher)
    actuators = start_actuators(pi_config, stop_event, publisher)
    cmd_handler = CommandHandler(actuators, threads, stop_event)

    print("[PI3] System ready.")

    try:
        while not stop_event.is_set():
            try:
                command = input(">>> ")
                cmd_handler.handle(command)
            except EOFError:
                stop_event.set()
                break

    except KeyboardInterrupt:
        stop_event.set()
        publisher.stop_event.set()

    finally:
        print("[PI3] Stopping publisher...")
        publisher.shutdown()

        print("[PI3] Waiting for threads to finish...")
        for t in threads:
            if t.is_alive():
                t.join(timeout=2)

        print("[PI3] Shutdown complete")
