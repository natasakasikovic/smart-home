import random
import time
import threading
import math
from ..base.gsg_interface import GSGInterface


def loop(gsg):
    gsg.log("GSG simulation started")
    while not gsg.should_stop():
        data = gsg.read_sensor_data()

        if data is not None:
            # Only send callback if there's a significant change
            if gsg.has_significant_change(data["accel"], data["gyro"]):
                gsg.callback(data, gsg.config)
                if gsg.config.get("verbose", False):
                    gsg.log("[GSG SIM] Significant change detected - sending update (SIMULATED GSG)")

        time.sleep(gsg.config.get('poll_interval', 0.1))

    gsg.log("GSG simulation loop stopped")


class GSG(GSGInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.log("Initializing GSG (Gyroscope) simulation - MPU6050 simulated")
        
        # Simulation state
        self.time_offset = 0
        self.base_accel = [0, 0, 16384]  # Gravity on Z-axis
        self.base_gyro = [0, 0, 0]
        self.movement_intensity = 0.0

    def read_sensor_data(self) -> dict:
        """
        Simulates accelerometer and gyroscope data.
        Periodically simulates movement bursts.
        """
        self.time_offset += self.config.get('poll_interval', 0.1)
        
        # Randomly trigger movement bursts
        if random.random() < 0.05:  # 5% chance each reading
            self.movement_intensity = random.uniform(0.5, 1.5)
            if self.config.get("verbose", False):
                self.log(f"[SIM] Movement burst triggered (intensity: {self.movement_intensity:.2f})")
        
        # Decay movement intensity
        self.movement_intensity *= 0.95
        
        # Simulate accelerometer data
        movement_factor = int(self.movement_intensity * 1000)
        accel = [
            self.base_accel[0] + random.randint(-100, 100) + int(math.sin(self.time_offset) * movement_factor),
            self.base_accel[1] + random.randint(-100, 100) + int(math.cos(self.time_offset) * movement_factor),
            self.base_accel[2] + random.randint(-50, 50)
        ]
        
        # Simulate gyroscope data
        gyro = [
            self.base_gyro[0] + random.randint(-50, 50) + int(math.sin(self.time_offset * 2) * movement_factor * 0.5),
            self.base_gyro[1] + random.randint(-50, 50) + int(math.cos(self.time_offset * 2) * movement_factor * 0.5),
            self.base_gyro[2] + random.randint(-30, 30)
        ]
        
        # Convert to g and degrees per second
        accel_g = [accel[0]/16384.0, accel[1]/16384.0, accel[2]/16384.0]
        gyro_dps = [gyro[0]/131.0, gyro[1]/131.0, gyro[2]/131.0]

        return {
            "accel": accel,
            "gyro": gyro,
            "accel_g": accel_g,
            "gyro_dps": gyro_dps
        }

    def start(self):
        thread = threading.Thread(
            target=loop,
            args=(self,),
            name=f"GSG-{self.config.get('name', 'unknown')}"
        )
        thread.daemon = True
        thread.start()
        self.log("GSG simulation thread started")
        return thread

    def log(self, message: str) -> None:
        super().log(message)

    def should_stop(self):
        return super().should_stop()