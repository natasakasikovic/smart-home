import threading, signal,json

from components.ds_manager import DSManager
from components.dms_manager import DMSManager
from components.dpir_manager import DPIRManager
from components.db_manager import DBManager
from components.dl_manager import DLManager
from components.dus_manager import DUSManager
from controllers.pi1.command_handler import CommandHandler

import command_listener

from publisher import Publisher
from utils.config_loader import load_config

def start_sensors(config, stop_event, publisher):
    threads = []

    if "DS1" in config:
        ds1_config = config["DS1"]
        ds1_config["code"] = "DS1"
        threads.append(
            DSManager.start_ds(ds1_config, stop_event, publisher)
        )

    if "DMS" in config:
        dms_config = config["DMS"]
        dms_config["code"] = "DMS"
        threads.append(
            DMSManager.start_dms(dms_config, stop_event, publisher)
        )

    if "DPIR1" in config:
        dpir1_config = config["DPIR1"]
        dpir1_config["code"] = "DPIR1"
        threads.append(
            DPIRManager.start_dpir(dpir1_config, stop_event, publisher)
        )

    if "DUS1" in config:
        dus1_config = config["DUS1"]
        dus1_config["code"] = "DUS1"
        threads.append(
            DUSManager.start_dus(dus1_config, stop_event, publisher)
        )

    return threads


def start_actuators(config, stop_event, publisher):
    actuators = {}

    if "DB" in config:
        db_config = config["DB"]
        db_config["code"] = "DB"
        actuators["DB"] = DBManager.start_db(db_config, stop_event, publisher)

    if "DL" in config:
        dl_config = config["DL"]
        dl_config["code"] = "DL"
        actuators["DL"] = DLManager.start_dl(dl_config, stop_event, publisher)

    return actuators


def run():
    print("[PI1] Starting...")

    config = load_config("config/settings.json")
    pi_config = config["PI1"]

    stop_event = threading.Event()

    signal.signal(signal.SIGINT, lambda s, f: stop_event.set())
    signal.signal(signal.SIGTERM, lambda s, f: stop_event.set())

    publisher = Publisher(config["mqtt"])
    publisher.start_daemon()

    threads = start_sensors(pi_config, stop_event, publisher)
    actuators = start_actuators(pi_config, stop_event, publisher)
    cmd_client = command_listener.start(actuators, config["mqtt"]["hostname"], config["mqtt"]["port"], client_id="cmd-listener-pi1")


    cmd_handler = CommandHandler(actuators, threads, stop_event)

    print("[PI1] System ready. Type 'help' for commands.")

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
        print("[PI1] Stopping publisher...")
        publisher.shutdown()
        command_listener.stop(cmd_client)
        
        print("[PI1] Waiting for sensor threads to finish...")
        for t in threads:
            if t.is_alive():
                t.join(timeout=2)
        
        print("[PI1] Shutdown complete")