import threading
import time
from typing import Tuple

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from ...base.dht_interface import DHTInterface

DHTLIB_OK = 0
DHTLIB_ERROR_CHECKSUM = -1
DHTLIB_ERROR_TIMEOUT = -2
DHTLIB_INVALID_VALUE = -999

DHTLIB_DHT11_WAKEUP = 0.020
DHTLIB_TIMEOUT = 0.005


def loop(dht):
    if GPIO is None:
        raise RuntimeError("RPi.GPIO not available")

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    try:
        while not dht.stop_event.is_set():
            try:
                temperature, humidity = dht.read()

                dht.log(
                    f" REAL DHT - Temperature: {temperature:.2f}°C, "
                    f"Humidity: {humidity:.2f}%"
                )

                if dht.callback:
                    dht.callback({
                        "temperature": temperature,
                        "humidity": humidity
                    })

            except RuntimeError as e:
                dht.log(f"DHT read error: {e}")
                time.sleep(1)

            time.sleep(dht.interval)

    finally:
        GPIO.cleanup(dht.pin)
        dht.log("GPIO cleaned up for DHT")


class DHT(DHTInterface):
    def __init__(self, config, stop_event, callback=None):
        super().__init__(config, stop_event, callback)

        if GPIO is None:
            raise RuntimeError("RPi.GPIO not available")

        self.pin = config["pin"]
        self.interval = config.get("interval", 2)

        self.bits = [0, 0, 0, 0, 0]

        self.log(f"Initializing real DHT11 on pin {self.pin}")

    def start(self):
        t = threading.Thread(target=loop, args=(self,), daemon=True)
        t.start()
        return t

    def read(self) -> Tuple[float, float]:
        rv = self._read_sensor()

        if rv != DHTLIB_OK:
            # print("Sensor return value:", rv)
            raise RuntimeError("Failed to read DHT sensor")

        humidity = self.bits[0]
        temperature = self.bits[2] + self.bits[3] * 0.1

        checksum = (
            self.bits[0]
            + self.bits[1]
            + self.bits[2]
            + self.bits[3]
        ) & 0xFF

        if self.bits[4] != checksum:
            raise RuntimeError("Checksum error")

        return temperature, humidity

    def _read_sensor(self):
        mask = 0x80
        idx = 0
        self.bits = [0, 0, 0, 0, 0]

        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        time.sleep(DHTLIB_DHT11_WAKEUP)
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(0.00004)
        GPIO.setup(self.pin, GPIO.IN)

        loop_cnt = DHTLIB_TIMEOUT

        t = time.perf_counter()
        while GPIO.input(self.pin) == GPIO.LOW:
            if (time.perf_counter() - t) > loop_cnt:
                return DHTLIB_ERROR_TIMEOUT

        t = time.perf_counter()
        while GPIO.input(self.pin) == GPIO.HIGH:
            if (time.perf_counter() - t) > loop_cnt:
                return DHTLIB_ERROR_TIMEOUT

        for _ in range(40):
            t = time.perf_counter()
            while GPIO.input(self.pin) == GPIO.LOW:
                if (time.perf_counter() - t) > loop_cnt:
                    return DHTLIB_ERROR_TIMEOUT

            t = time.perf_counter()
            while GPIO.input(self.pin) == GPIO.HIGH:
                if (time.perf_counter() - t) > loop_cnt:
                    return DHTLIB_ERROR_TIMEOUT

            if (time.perf_counter() - t) > 0.00005:
                self.bits[idx] |= mask

            mask >>= 1
            if mask == 0:
                mask = 0x80
                idx += 1

        return DHTLIB_OK
