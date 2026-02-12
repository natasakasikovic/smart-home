import time
import threading

from ...real.gsg import MPU6050
from ...base.gsg_interface import GSGInterface

def loop(gsg):
    gsg.log("REAL GSG loop started")

    while not gsg.should_stop():
        data = gsg.read_sensor_data()

        if data is not None:
            # Only send callback if there's a significant change
            if gsg.has_significant_change(data["accel"], data["gyro"]):
                gsg.callback(data, gsg.config)
                if gsg.config.get("verbose", False):
                    gsg.log("Significant change detected - sending update")

        time.sleep(gsg.config.get("poll_interval", 0.1))

    gsg.cleanup()
    gsg.log("REAL GSG loop stopped")


class GSG(GSGInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)

        self.log("Initializing REAL GSG (Gyroscope) - MPU6050")

        if MPU6050 is None:
            raise ImportError("MPU6050 library not available. Install it to use real GSG.")

        try:
            self.mpu = MPU6050.MPU6050()
            self.mpu.dmp_initialize()
            self.log("MPU6050 initialized successfully")
        except Exception as e:
            self.log(f"Error initializing MPU6050: {e}")
            raise

    def read_sensor_data(self) -> dict:
        """Reads accelerometer and gyroscope data from MPU6050"""
        try:
            accel = self.mpu.get_acceleration()
            gyro = self.mpu.get_rotation()

            # Convert to g and degrees per second
            accel_g = [accel[0]/16384.0, accel[1]/16384.0, accel[2]/16384.0]
            gyro_dps = [gyro[0]/131.0, gyro[1]/131.0, gyro[2]/131.0]

            return {
                "accel": accel,
                "gyro": gyro,
                "accel_g": accel_g,
                "gyro_dps": gyro_dps
            }

        except Exception as e:
            self.log(f"Error reading sensor data: {e}")
            return None

    def start(self):
        thread = threading.Thread(
            target=loop,
            args=(self,),
            name=f"GSG-{self.config.get('name', 'unknown')}",
            daemon=True
        )
        thread.start()
        self.log("REAL GSG thread started")
        return thread

    def cleanup(self):
        self.log("Cleaning up MPU6050")

    def log(self, message: str) -> None:
        super().log(message)

    def should_stop(self):
        return super().should_stop()