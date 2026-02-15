import threading
import signal

from publisher import Publisher
from utils.config_loader import load_config
from components.gsg_manager import GSGManager
from components.ssd_manager import SSDManager
from controllers.pi2.command_handler import CommandHandler

def start_sensors(config, stop_event, publisher):
    sensors = []
    if "GSG" in config:
      gsg_config = config["GSG"]
      gsg_config["code"] = "GSG"
      sensors.append(
          GSGManager.start_gsg(gsg_config, stop_event, publisher)
      )
    return sensors


def start_actuators(config, stop_event, publisher):
    
    actuators = {}
    if "4SD" in config:
        ssd_config = config["4SD"]
        ssd_config["code"] = "4SD"
        ssd = SSDManager.start_ssd(ssd_config, stop_event, publisher)
        actuators["4SD"] = ssd

    return actuators


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

    cmd_handler = CommandHandler(actuators, threads, stop_event)

    print("[PI2] System ready. Type 'help' for commands.")

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
        print("[PI2] Stopping publisher...")
        publisher.shutdown()

        print("[PI2] Waiting for threads to finish...")
        for t in threads:
            if t.is_alive():
                t.join(timeout=2)

        print("[PI2] Shutdown complete")
