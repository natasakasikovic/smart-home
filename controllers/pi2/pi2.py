import threading
import signal

import command_listener

from publisher import Publisher
from utils.config_loader import load_config
from components.gsg_manager import GSGManager
from components.ssd_manager import SSDManager
from components.dht_manager import DHTManager
from components.ds_manager import DSManager
from components.dus_manager import DUSManager
from components.dpir_manager import DPIRManager
from controllers.pi2.command_handler import CommandHandler

def start_sensors(config, stop_event, publisher):
    sensors = []

    if "DS2" in config:
        ds2_config = config["DS2"]
        ds2_config["code"] = "DS2"
        sensors.append(
            DSManager.start_ds(ds2_config, stop_event, publisher)
        )
    
    if "DUS2" in config:
        dus2_config = config["DUS2"]
        dus2_config["code"] = "DUS2"
        sensors.append(
            DUSManager.start_dus(dus2_config, stop_event, publisher)
        )

    if "DPIR2" in config:
        dpir2_config = config["DPIR2"]
        dpir2_config["code"] = "DPIR2"
        sensors.append(
            DPIRManager.start_dpir(dpir2_config, stop_event, publisher)
        )

    if "GSG" in config:
      gsg_config = config["GSG"]
      gsg_config["code"] = "GSG"
      sensors.append(
          GSGManager.start_gsg(gsg_config, stop_event, publisher)
      )

    if "DHT3" in config:
        dht1_config = config["DHT3"]
        dht1_config["code"] = "DHT3"
        sensors.append(
            DHTManager.start_dht(dht1_config, stop_event, publisher)
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
    cmd_client = command_listener.start(actuators, config["mqtt"]["hostname"], config["mqtt"]["port"], client_id="cmd-listener-pi2")

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
        command_listener.stop(cmd_client)

        print("[PI2] Waiting for threads to finish...")
        for t in threads:
            if t.is_alive():
                t.join(timeout=2)

        print("[PI2] Shutdown complete")
