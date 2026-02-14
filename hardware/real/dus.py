from hardware.base.dus_interface import DUSInterface
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None


def loop(dus):
    dus.log("REAL DUS loop started")

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(dus.trig_pin, GPIO.OUT)
    GPIO.setup(dus.echo_pin, GPIO.IN)

    GPIO.output(dus.trig_pin, False)
    time.sleep(0.1)

    while not dus.should_stop():
        distance = dus.detect()

        if distance is not None:
            dus.callback(distance, dus.config)

        time.sleep(dus.config.get("poll_interval", 0.1))

    GPIO.cleanup([dus.trig_pin, dus.echo_pin])
    dus.log("REAL DUS loop stopped")


class DUS(DUSInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.trig_pin = config["trig_pin"]
        self.echo_pin = config["echo_pin"]

        self.log("Initializing REAL DUS (Door Ultrasonic Sensor)")

    def detect(self):
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)

        timeout = 0.02  

        start_wait = time.perf_counter()
        while GPIO.input(self.echo_pin) == 0:
            if time.perf_counter() - start_wait > timeout:
                return None

        pulse_start = time.perf_counter()

        # Wait for echo LOW
        while GPIO.input(self.echo_pin) == 1:
            if time.perf_counter() - pulse_start > timeout:
                return None

        pulse_end = time.perf_counter()

        pulse_duration = pulse_end - pulse_start

        if pulse_duration <= 0:
            return None

        distance = (pulse_duration * 34300) / 2  # cm

        self.log(f"REAL DUS detected distance: {distance:.2f} cm")
        return round(distance, 2)

    def start(self):
        import threading

        thread = threading.Thread(
            target=loop,
            args=(self,),
            name=f"DUS-{self.config.get('name', 'unknown')}",
            daemon=True,
        )
        thread.start()
        self.log("REAL DUS thread started")
        return thread
