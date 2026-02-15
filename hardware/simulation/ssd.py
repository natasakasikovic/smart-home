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
        self.display_buffer = " " * self.digits
        self.log(f"Initializing simulated {self.digits}-digit 7-segment display")
    
    def display_number(self, value: str):
        allowed = "0123456789"
        filtered = ''.join(c for c in str(value) if c in allowed)
        filtered = filtered.rjust(self.digits)[:self.digits]
        
        self.display_buffer = filtered
        self._print_display()
        # self.log(f"[SIMULATED] Displaying: {filtered}")
        
        if self.callback:
            self.callback({"action": "display", "value": filtered}, self.config)
    
    def clear(self):
        self.display_buffer = " " * self.digits
        self._print_display()
        self.log("[SIMULATED] Display cleared")
        if self.callback:
            self.callback({"action": "clear"}, self.config)
    
    def _print_display(self):
        border = "+" + "-"*self.digits + "+"
        print(border)
        print(f"|{self.display_buffer}|")
        print(border)
    
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