import time
import threading

from ...real.gsg.MPU6050 import MPU6050
from ...base.gsg_interface import GSGInterface


def loop(gsg):
    gsg.log("REAL GSG loop started")

    while not gsg.should_stop():
        try:
            accel = gsg.mpu.get_acceleration()
            gyro = gsg.mpu.get_rotation()

            data = {
                "accel": accel,
                "gyro": gyro,
                "accel_g": [accel[0] / 16384.0, accel[1] / 16384.0, accel[2] / 16384.0],
                "gyro_dps": [gyro[0] / 131.0, gyro[1] / 131.0, gyro[2] / 131.0],
            }
            if gsg.config.get("verbose", False):
                gsg.log(f"Accel (raw): {accel[0]:6d} {accel[1]:6d} {accel[2]:6d}")
                gsg.log(f"Gyro  (raw): {gyro[0]:6d} {gyro[1]:6d} {gyro[2]:6d}")
                gsg.log(f"Accel (g):   {data['accel_g'][0]:6.2f} {data['accel_g'][1]:6.2f} {data['accel_g'][2]:6.2f}")
                gsg.log(f"Gyro  (°/s): {data['gyro_dps'][0]:6.2f} {data['gyro_dps'][1]:6.2f} {data['gyro_dps'][2]:6.2f}")

            if gsg.has_significant_change(data["accel"], data["gyro"]):
                gsg.callback(data, gsg.config)

                if gsg.config.get("verbose", False):
                    gsg.log("Significant change detected - sending update")

        except Exception as e:
            gsg.log(f"Error reading sensor data: {e}")

        time.sleep(gsg.config.get("poll_interval", 0.1))

    gsg.cleanup()
    gsg.log("REAL GSG loop stopped")


class GSG(GSGInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)

        self.log("Initializing REAL GSG (Gyroscope) - MPU6050")

        try:
            self.mpu = MPU6050()
            self.mpu.dmp_initialize()
            self.log("MPU6050 initialized successfully")

        except Exception as e:
            self.log(f"Error initializing MPU6050: {e}")
            raise

    def start(self):
        thread = threading.Thread(
            target=loop,
            args=(self,),
            name=f"GSG-{self.config.get('name', 'Gyroscope')}",
            daemon=True
        )
        thread.start()
        self.log("REAL GSG thread started")
        return thread

    def cleanup(self):
        self.log("Cleaning up MPU6050")