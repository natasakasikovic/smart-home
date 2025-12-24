from hardware.base.dus_interface import DUSInterface
import time, RPi.GPIO as GPIO

def loop(dus):
    dus.log("REAL DUS loop started")

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(dus.trig_pin, GPIO.OUT)
    GPIO.setup(dus.echo_pin, GPIO.IN)

    while not dus.should_stop():
        distance = dus.detect() 

        if distance is not None:
            dus.callback(distance, dus.config)
        time.sleep(dus.config.get("poll_interval", 0.1))
    
    dus.log("REAL DUS loop stopped")

class DUS(DUSInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.trig_pin = config['trig_pin']
        self.echo_pin = config['echo_pin']
        self.log("Initializing REAL DUS (Door Ultrasonic Sensor")

    def detect(self):
        GPIO.output(self.trig_pin, False)
        time.sleep(0.2)
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)
        pulse_start_time = time.time()
        pulse_end_time = time.time()

        max_iter = 100

        iter = 0
        while GPIO.input(self.echo_pin) == 0:
            if iter > max_iter:
                return None
            pulse_start_time = time.time()
            iter += 1

        iter = 0
        while GPIO.input(self.echo_pin) == 1:
            if iter > max_iter:
                return None
            pulse_end_time = time.time()
            iter += 1

        pulse_duration = pulse_end_time - pulse_start_time
        distance = (pulse_duration * 34300)/2
        return distance