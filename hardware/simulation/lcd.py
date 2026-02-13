import time
import threading
from ..base.lcd_interface import LCDInterface


def loop(lcd_obj):
    lcd_obj.log("Simulated LCD loop started")
    while not lcd_obj.should_stop():
        time.sleep(1)
    lcd_obj.log("Simulated LCD loop stopped")
    
class LCD(LCDInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.display_buffer = [" " * self.columns for _ in range(self.rows)]
        self.log(f"Initializing simulated LCD ({self.columns}x{self.rows})")

    def display_text(self, text: str, line: int = 0) -> None:
        if line < 0 or line >= self.rows:
            self.log(f"Invalid line number: {line}")
            return
        
        display_text = text[:self.columns].ljust(self.columns)
        self.display_buffer[line] = display_text
        
        self._print_display()
        self.log(f"[SIMULATED] Displayed text on line {line}: {text}")
        
        if self.callback:
            self.callback({
                "action": "display",
                "line": line,
                "text": text
            }, self.config)


    def clear(self) -> None:
        self.display_buffer = [" " * self.columns for _ in range(self.rows)]
        self._print_display()
        self.log("[SIMULATED] LCD cleared")
        
        if self.callback:
            self.callback({
                "action": "clear"
            }, self.config)


    def change_backlight_state(self, state: bool) -> None:
        self.backlight_on = state
        self.log(f"[SIMULATED] Backlight {'ON' if state else 'OFF'}")
        
        if self.callback:
            self.callback({
                "action": "backlight",
                "state": state
            }, self.config)


    def set_cursor(self, col: int, row: int) -> None:
        if col < 0 or col >= self.columns or row < 0 or row >= self.rows:
            self.log(f"[SIMULATED] Invalid cursor position: ({col}, {row})")
            return
        
        self.log(f"[SIMULATED] Cursor set to ({col}, {row})")


    def _print_display(self):
        border = "+" + "-" * self.columns + "+"
        print(border)
        for row in self.display_buffer:
            print(f"|{row}|")
        print(border)


    def get_cpu_temp(self):
        return '42.50 C'
    

    def get_time_now(self):
        from datetime import datetime
        return datetime.now().strftime('%H:%M:%S')
    

    def start(self):
        thread = threading.Thread(
            target=loop,
            args=(self,),
            name="LCD-simulated"
        )
        thread.daemon = True
        thread.start()
        self.log("Simulated LCD thread started")
        return thread
    

    def cleanup(self):
        self.clear()
        self.log("[SIMULATED] LCD cleaned up")


    def log(self, message: str) -> None:
        super().log(message)


    def should_stop(self):
        return super().should_stop()