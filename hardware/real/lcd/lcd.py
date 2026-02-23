import time
import threading

from ...real.lcd.PCF8574 import PCF8574_GPIO
from ...real.lcd.Adafruit_LCD1602 import Adafruit_CharLCD

from ...base.lcd_interface import LCDInterface


def loop(lcd_obj):
    lcd_obj.log("Real LCD loop started")
    while not lcd_obj.should_stop():
        time.sleep(1)
    lcd_obj.log("Real LCD loop stopped")


class LCD(LCDInterface):
    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.i2c_address = int(config.get("i2c_address", "0x27"), 16)
        self.i2c_address_alt = int(config.get("i2c_address_alt", "0x3F"), 16)
        self._lock = threading.Lock()
        
        try:
            self.mcp = PCF8574_GPIO(self.i2c_address)
            self.log(f"PCF8574 initialized at address {hex(self.i2c_address)}")
        except:

            try:
                self.mcp = PCF8574_GPIO(self.i2c_address_alt)
                self.log(f"PCF8574 initialized at alternate address {hex(self.i2c_address_alt)}")
            except:
                raise Exception('I2C Address Error - Could not initialize PCF8574')

        self.lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=self.mcp)
        
        self.mcp.output(3, 1)
        self.lcd.begin(self.columns, self.rows)
        
        self.log(f"Initializing REAL LCD ({self.columns}x{self.rows})")


    def display_text(self, text: str, line: int = 0) -> None:
        if line < 0 or line >= self.rows:
            if self.config.get("verbose", False): 
                self.log(f"Invalid line number: {line}")
            return
        
        display_text = text[:self.columns].ljust(self.columns)
        
        with self._lock: 
            self.set_cursor(0, line)
            self.lcd.message(display_text)
        
        self.log(f"Displayed text on line {line}: {text}")
        
        if self.callback:
            self.callback({
                "action": "display",
                "line": line,
                "text": text
            }, self.config)


    def display_both(self, line0: str, line1: str) -> None:
        with self._lock:
            self.set_cursor(0, 0)
            self.lcd.message(line0[:self.columns].ljust(self.columns))
            self.set_cursor(0, 1)
            self.lcd.message(line1[:self.columns].ljust(self.columns))
        
        # self.log(f"Displayed both lines: '{line0}' / '{line1}'")
        
        if self.callback:
            self.callback({
                "action": "display_both",
                "line0": line0,
                "line1": line1
            }, self.config)


    def clear(self) -> None:
        self.lcd.clear()
        self.log("LCD cleared")
        
        if self.callback:
            self.callback({
                "action": "clear"
            }, self.config)


    def change_backlight_state(self, state: bool) -> None:
        self.backlight_on = state
        self.mcp.output(3, 1 if state else 0)
        self.log(f"Backlight {'ON' if state else 'OFF'}")
        
        if self.callback:
            self.callback({
                "action": "backlight",
                "state": state
            }, self.config)


    def set_cursor(self, col: int, row: int) -> None:
        if col < 0 or col >= self.columns or row < 0 or row >= self.rows:
            self.log(f"Invalid cursor position: ({col}, {row})")
            return
        
        self.lcd.setCursor(col, row)


    def get_cpu_temp(self):
        try:
            with open('/sys/class/thermal/thermal_zone0/temp') as tmp:
                cpu = tmp.read()
                return '{:.2f}'.format(float(cpu)/1000) + ' C'
        except:
            return 'N/A'
        

    def get_time_now(self):
        from datetime import datetime
        return datetime.now().strftime('%H:%M:%S')

    def start(self):
        thread = threading.Thread(
            target=loop,
            args=(self,),
            name="LCD-real"
        )
        thread.daemon = True
        thread.start()
        self.log("Real LCD thread started")
        return thread


    def cleanup(self):
        self.clear()
        self.change_backlight_state(False)
        self.log("LCD cleaned up")


    def log(self, message: str) -> None:
        super().log(message)


    def should_stop(self):
        return super().should_stop()