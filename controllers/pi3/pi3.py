import threading
import signal

from components.ir_manager import IRManager
from publisher import Publisher
from utils.config_loader import load_config
from components.dpir_manager import DPIRManager
from components.rgb_manager import RGBManager
from components.lcd_manager import LCDManager
from components.dht_manager import DHTManager
from controllers.pi3.command_handler import CommandHandler

import command_listener

def start_sensors(config, stop_event, publisher):
    threads = []
    
    if "DPIR3" in config:
        dpir1_config = config["DPIR3"]
        dpir1_config["code"] = "DPIR3"
        threads.append(
            DPIRManager.start_dpir(dpir1_config, stop_event, publisher)
        )

    if "DHT1" in config:
        dht1_config = config["DHT1"]
        dht1_config["code"] = "DHT1"
        threads.append(
            DHTManager.start_dht(dht1_config, stop_event, publisher)
        )
    
    if "DHT2" in config:
        dht2_config = config["DHT2"]
        dht2_config["code"] = "DHT2"
        threads.append(
            DHTManager.start_dht(dht2_config, stop_event, publisher)
        )

    if "IR" in config:
        ir_config = config["IR"]
        ir_config["code"] = "IR"
        threads.append(
            IRManager.start_ir(ir_config, stop_event, publisher)
        )
    
    return threads

def start_actuators(config, stop_event, publisher):
    actuators = {}
    if "RGB" in config:
        rgb_config = config["RGB"]
        rgb_config["code"] = "RGB"
        rgb = RGBManager.start_rgb(rgb_config, stop_event, publisher)
        actuators["RGB"] = rgb

    if "LCD" in config:
        db_config = config["LCD"]
        db_config["code"] = "LCD"
        actuators["LCD"] = LCDManager.start_lcd(db_config, stop_event, publisher)

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

    cmd_client = command_listener.start(actuators, config["mqtt"]["hostname"], config["mqtt"]["port"], client_id="cmd-listener-pi3")

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
        command_listener.stop(cmd_client)

        print("[PI3] Waiting for threads to finish...")
        for t in threads:
            if t.is_alive():
                t.join(timeout=2)

        print("[PI3] Shutdown complete")
