from abc import abstractmethod
from hardware.base.sensor_interface import SensorInterface


class GSGInterface(SensorInterface):

    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.accel = [0, 0, 0]
        self.gyro = [0, 0, 0]
        self.last_accel = [0, 0, 0]
        self.last_gyro = [0, 0, 0]

    def has_significant_change(self, current_accel, current_gyro) -> bool:
        accel_threshold = self.config.get("accel_threshold", 2000)   
        gyro_threshold = self.config.get("gyro_threshold", 1000)     

        # Check accelerometer change
        accel_change = any(
            abs(current_accel[i] - self.last_accel[i]) > accel_threshold
            for i in range(3)
        )

        # Check gyroscope change
        gyro_change = any(
            abs(current_gyro[i] - self.last_gyro[i]) > gyro_threshold
            for i in range(3)
        )

        if accel_change or gyro_change:
            self.last_accel = current_accel[:]
            self.last_gyro = current_gyro[:]
            return True

        return False