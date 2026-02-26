import time
import threading
from ..base.ssd_interface import SSDInterface

def loop(display_obj):
    display_obj.log("Simulated 7-Segment loop started")
    
    while not display_obj.should_stop():
        current_time = time.strftime("%H%M")
        display_obj.display_number(current_time)
        time.sleep(1)
    
    display_obj.log("Simulated 7-Segment loop stopped")


class SSD(SSDInterface):    
    
    def __init__(self, config, stop_event, callback=None):
        super().__init__(config, stop_event, callback)
        self.digits = 4
        self.display_buffer = "0000"
        self.log(f"Initializing simulated {self.digits}-digit 7-segment display")
    
    def display_time(self, value: str):
        filtered = ''.join(c for c in str(value) if c.isdigit())
        filtered = filtered[-4:].rjust(4, '0')
        self.display_buffer = filtered
        
        self._print_display()
        
        if self.callback:
            self.callback({"action": "display", "value": filtered}, self.config)
    
    def _print_display(self):
        buf = self.display_buffer.rjust(4, '0')
        display_str = f"{buf[:2]}:{buf[2:]}"
        border = "+" + "-"*len(display_str) + "+"
        print(border)
        print(f"|{display_str}|")
        print(border)
    
    def clear(self):
        self.display_buffer = "0000"
        self._print_display()
        self.log("[SIMULATED] Display cleared")
        if self.callback:
            self.callback({"action": "clear"}, self.config)
    
    def start(self):
        thread = threading.Thread(
            target=loop,
            args=(self,),
            name="7Segment-simulated"
        )
        thread.daemon = True
        thread.start()
        self.log("Simulated 7-Segment thread started")
        return thread
    
    def cleanup(self):
        self.clear()
        self.log("[SIMULATED] 7-Segment cleaned up")