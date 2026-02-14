import threading
import time

class CommandHandler:
    """Handles user commands for the PI3 system."""
    
    def __init__(self, actuators, threads, stop_event):
        self.actuators = actuators
        self.threads = threads
        self.stop_event = stop_event
        self.lcd_auto_update = False
        self.lcd_update_thread = None
        self.rgb_cycle_active = False
        self.rgb_cycle_thread = None
        self.commands = {
            'exit': self.cmd_exit,
            'e': self.cmd_exit,
            'quit': self.cmd_exit,
            'status': self.cmd_status,
            'lcd': self.cmd_lcd,
            'rgb': self.cmd_rgb,
            'help': self.cmd_help,
        }
    
    def cmd_exit(self, args):
        """Exit the application."""
        print("[PI3] Shutting down...")
        self.lcd_auto_update = False
        self.rgb_cycle_active = False
        self.stop_event.set()
    
    def cmd_status(self, args):
        """Show system status."""
        active = len([t for t in self.threads if t.is_alive()])
        print(f"[PI3] Active threads: {active}")
        print(f"[PI3] Active actuators: {list(self.actuators.keys())}")
        print(f"[PI3] LCD auto-update: {'ON' if self.lcd_auto_update else 'OFF'}")
        print(f"[PI3] RGB cycle: {'ON' if self.rgb_cycle_active else 'OFF'}")

    def cmd_lcd(self, args):
        """Control LCD actuator: lcd [on|off|clear|write|cpu|stop]"""
        
        if "LCD" not in self.actuators:
            print("[ERROR] LCD actuator not available")
            return
        
        if not args:
            print("Usage: lcd [on|off|clear|write|cpu|stop]")
            return
        
        action = args[0].lower()
        lcd = self.actuators["LCD"]
        
        if action == "on":
            lcd.change_backlight_state(True)
            print("[LCD] Backlight turned ON")
            
        elif action == "off":
            lcd.change_backlight_state(False)
            print("[LCD] Backlight turned OFF")
            
        elif action == "clear":
            lcd.clear()
            print("[LCD] Display cleared")
            
        elif action == "write":
            if len(args) < 3:
                print("Usage: lcd write <line> <text>")
                print("Example: lcd write 0 Hello World")
                return
            
            try:
                line = int(args[1])
                text = ' '.join(args[2:])
                lcd.display_text(text, line)
                print(f"[LCD] Written to line {line}: {text}")
            except ValueError:
                print("[ERROR] Line must be a number (0 or 1)")
            except Exception as e:
                print(f"[ERROR] Failed to write to LCD: {e}")
                
        elif action == "cpu":
            if self.lcd_auto_update:
                print("[LCD] Auto-update already running")
                return
                
            self.lcd_auto_update = True
            self.lcd_update_thread = threading.Thread(
                target=self._lcd_cpu_loop,
                args=(lcd,),
                name="LCD-CPU-Display",
                daemon=True
            )
            self.lcd_update_thread.start()
            print("[LCD] CPU/Time auto-update started")
            
        elif action == "stop":
            if not self.lcd_auto_update:
                print("[LCD] Auto-update is not running")
                return
                
            self.lcd_auto_update = False
            print("[LCD] Auto-update stopped")
            
        else:
            print(f"[ERROR] Unknown LCD action: {action}")

    def cmd_rgb(self, args):
        """Control RGB LED: rgb [off|red|green|blue|yellow|purple|cyan|white|cycle|stop]"""
        
        if "RGB" not in self.actuators:
            print("[ERROR] RGB actuator not available")
            return
        
        if not args:
            print("Usage: rgb [off|red|green|blue|yellow|purple|cyan|white|cycle|stop]")
            return
        
        action = args[0].lower()
        rgb = self.actuators["RGB"]
        
        if action == "off":
            self.rgb_cycle_active = False
            rgb.turn_off()
            print("[RGB] LED turned OFF 🌑")
            
        elif action == "red":
            self.rgb_cycle_active = False
            rgb.red()
            print("[RGB] LED set to RED 🔴")
            
        elif action == "green":
            self.rgb_cycle_active = False
            rgb.green()
            print("[RGB] LED set to GREEN 🟢")
            
        elif action == "blue":
            self.rgb_cycle_active = False
            rgb.blue()
            print("[RGB] LED set to BLUE 🔵")
            
        elif action == "yellow":
            self.rgb_cycle_active = False
            rgb.yellow()
            print("[RGB] LED set to YELLOW 🟡")
            
        elif action == "purple":
            self.rgb_cycle_active = False
            rgb.purple()
            print("[RGB] LED set to PURPLE 🟣")
            
        elif action == "cyan" or action == "lightblue":
            self.rgb_cycle_active = False
            rgb.light_blue()
            print("[RGB] LED set to CYAN 🔵💧")
            
        elif action == "white":
            self.rgb_cycle_active = False
            rgb.white()
            print("[RGB] LED set to WHITE ⚪")
            
        elif action == "cycle":
            if self.rgb_cycle_active:
                print("[RGB] Color cycle already running")
                return
                
            self.rgb_cycle_active = True
            self.rgb_cycle_thread = threading.Thread(
                target=self._rgb_cycle_loop,
                args=(rgb,),
                name="RGB-Color-Cycle",
                daemon=True
            )
            self.rgb_cycle_thread.start()
            print("[RGB] Color cycle started 🌈")
            
        elif action == "stop":
            if not self.rgb_cycle_active:
                print("[RGB] Color cycle is not running")
                return
                
            self.rgb_cycle_active = False
            print("[RGB] Color cycle stopped")
            
        else:
            print(f"[ERROR] Unknown RGB action: {action}")
            print("Available colors: off, red, green, blue, yellow, purple, cyan, white")

    def _lcd_cpu_loop(self, lcd):
        """Continuous loop to display CPU temperature and time on LCD"""
        lcd.change_backlight_state(True)
        
        while self.lcd_auto_update and not self.stop_event.is_set():
            try:
                cpu_temp = lcd.get_cpu_temp()
                time_now = lcd.get_time_now()
                
                lcd.set_cursor(0, 0)
                lcd.display_text(f"CPU: {cpu_temp}", line=0)
                lcd.set_cursor(0, 1)
                lcd.display_text(f"    {time_now}", line=1)
                
                time.sleep(1)
            except Exception as e:
                print(f"[ERROR] LCD update failed: {e}")
                self.lcd_auto_update = False
                break

    def _rgb_cycle_loop(self, rgb):
        """Continuous loop to cycle through RGB colors"""
        colors = [
            ("OFF", rgb.turn_off),
            ("WHITE", rgb.white),
            ("RED", rgb.red),
            ("GREEN", rgb.green),
            ("BLUE", rgb.blue),
            ("YELLOW", rgb.yellow),
            ("PURPLE", rgb.purple),
            ("CYAN", rgb.light_blue),
        ]
        
        color_index = 0
        
        while self.rgb_cycle_active and not self.stop_event.is_set():
            try:
                color_name, color_func = colors[color_index]
                color_func()
                # print(f"[RGB] Cycled to {color_name}")
                
                color_index = (color_index + 1) % len(colors)
                time.sleep(1)
                
            except Exception as e:
                print(f"[ERROR] RGB cycle failed: {e}")
                self.rgb_cycle_active = False
                break
    
    def cmd_help(self, args):
        """Show available commands."""
        print("\n[PI3] Available commands:")
        print("  exit, quit, e           - Exit the application")
        print("  status                  - Show system status")
        print("\n  LCD Commands:")
        print("  lcd on                  - Turn LCD backlight ON")
        print("  lcd off                 - Turn LCD backlight OFF")
        print("  lcd clear               - Clear LCD display")
        print("  lcd write <line> <text> - Write text to line (0 or 1)")
        print("  lcd cpu                 - Start CPU temp/time auto-update")
        print("  lcd stop                - Stop auto-update")
        print("\n  RGB LED Commands:")
        print("  rgb off                 - Turn RGB LED OFF")
        print("  rgb red                 - Set color to RED")
        print("  rgb green               - Set color to GREEN")
        print("  rgb blue                - Set color to BLUE")
        print("  rgb yellow              - Set color to YELLOW")
        print("  rgb purple              - Set color to PURPLE")
        print("  rgb cyan                - Set color to CYAN")
        print("  rgb white               - Set color to WHITE")
        print("  rgb cycle               - Start color cycling")
        print("  rgb stop                - Stop color cycling")
        print("\n  help                    - Show this help message")
        print("  exit, quit, e          - Exit the application")
        print("  status                 - Show system status")
        print("  lcd on                 - Turn LCD backlight ON")
        print("  lcd off                - Turn LCD backlight OFF")
        print("  lcd clear              - Clear LCD display")
        print("  lcd write <line> <text> - Write text to line (0 or 1)")
        print("  lcd cpu                - Start CPU temp/time auto-update")
        print("  lcd stop               - Stop auto-update")
        print("  help                   - Show this help message")
        print()
    
    def handle(self, command_line):
        parts = command_line.strip().lower().split()
        if not parts:
            return
        
        cmd = parts[0]
        args = parts[1:]
        
        if cmd in self.commands:
            self.commands[cmd](args)
        else:
            print(f"[ERROR] Unknown command: {cmd}")
            print("Type 'help' for available commands")