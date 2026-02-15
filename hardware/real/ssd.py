import RPi.GPIO as GPIO
import time
import threading
from ..base.ssd_interface import SSDInterface

def loop(display_obj):
    display_obj.log("Real 7-Segment loop started")
    
    while not display_obj.should_stop():
        current_time = time.strftime("%H%M")
        display_obj.display_number(current_time)
        time.sleep(1)
    
    display_obj.log("Real 7-Segment loop stopped")


class SSD(SSDInterface):
    
    def __init__(self, config, stop_event, callback=None):
        super().__init__(config, stop_event, callback)
        
        self.segments = tuple(config.get("segments", (11,4,23,8,7,10,18,25)))
        self.digits = tuple(config.get("digits", (22,27,17,24)))
        self.dp_pin = config.get("dp_pin", 25)  
        
        self.num_map = {
            ' ': (0,0,0,0,0,0,0),
            '0': (1,1,1,1,1,1,0),
            '1': (0,1,1,0,0,0,0),
            '2': (1,1,0,1,1,0,1),
            '3': (1,1,1,1,0,0,1),
            '4': (0,1,1,0,0,1,1),
            '5': (1,0,1,1,0,1,1),
            '6': (1,0,1,1,1,1,1),
            '7': (1,1,1,0,0,0,0),
            '8': (1,1,1,1,1,1,1),
            '9': (1,1,1,1,0,1,1)
        }
        
        GPIO.setmode(GPIO.BCM)
        for seg in self.segments:
            GPIO.setup(seg, GPIO.OUT)
            GPIO.output(seg, 0)
        for digit in self.digits:
            GPIO.setup(digit, GPIO.OUT)
            GPIO.output(digit, 1)
        GPIO.setup(self.dp_pin, GPIO.OUT)
        GPIO.output(self.dp_pin, 0)
        
        self.display_buffer = " " * len(self.digits)
        self.log("GPIO 7-Segment initialized")
    
    def display_number(self, value: str) -> None:
        value = str(value).rjust(len(self.digits))[:len(self.digits)]
        self.display_buffer = value
        
        for digit_idx in range(len(self.digits)):
            for seg_idx in range(7):
                GPIO.output(self.segments[seg_idx], self.num_map[value[digit_idx]][seg_idx])
            if self.dp_pin and int(time.time()) % 2 == 0 and digit_idx == 1:
                GPIO.output(self.dp_pin, 1)
            else:
                GPIO.output(self.dp_pin, 0)
            GPIO.output(self.digits[digit_idx], 0)
            time.sleep(0.001)
            GPIO.output(self.digits[digit_idx], 1)
        
        # self.log(f"Displayed: {value}")
        
        if self.callback:
            self.callback({"action": "display", "value": value}, self.config)
    
    def clear(self) -> None:
        self.display_buffer = " " * len(self.digits)
        for seg in self.segments:
            GPIO.output(seg, 0)
        for digit in self.digits:
            GPIO.output(digit, 1)
        if self.dp_pin:
            GPIO.output(self.dp_pin, 0)
        # self.log("Display cleared")
        
        if self.callback:
            self.callback({"action": "clear"}, self.config)
    
    def start(self):
        thread = threading.Thread(target=loop, args=(self,), name="7Segment-real")
        thread.daemon = True
        thread.start()
        self.log("Real 7-Segment thread started")
        return thread
    
    def cleanup(self) -> None:
        self.clear()
        GPIO.cleanup()
        self.log("7-Segment cleaned up")