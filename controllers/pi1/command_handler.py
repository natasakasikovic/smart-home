class CommandHandler:
    """Handles user commands for the PI1 system."""
    
    def __init__(self, actuators, threads, stop_event):
        self.actuators = actuators
        self.threads = threads
        self.stop_event = stop_event
        self.commands = {
            'exit': self.cmd_exit,
            'e': self.cmd_exit,
            'quit': self.cmd_exit,
            'status': self.cmd_status,
            'db': self.cmd_db,
            'dl': self.cmd_dl,
            'help': self.cmd_help,
        }
    
    def cmd_exit(self, args):
        """Exit the application."""
        print("[PI1] Shutting down...")
        self.stop_event.set()
    
    def cmd_status(self, args):
        """Show system status."""
        active = len([t for t in self.threads if t.is_alive()])
        print(f"[PI1] Active threads: {active}")
        print(f"[PI1] Active actuators: {list(self.actuators.keys())}")
    
    def cmd_db(self, args):
        """Control DB actuator: db [on|off|beep <duration>]"""
        if "DB" not in self.actuators:
            print("[ERROR] DB actuator not available")
            return
        
        if not args:
            print("Usage: db [on|off|beep <duration>]")
            return
        
        action = args[0]
        
        if action == "on":
            self.actuators["DB"].on()
        elif action == "off":
            self.actuators["DB"].off()
        elif action == "beep":
            if len(args) < 2:
                print("Usage: db beep <seconds>")
                return
            try:
                duration = float(args[1])
                self.actuators["DB"].beep(duration)
            except ValueError:
                print("[ERROR] Duration must be a number")
        else:
            print(f"[ERROR] Unknown DB action: {action}")

    def cmd_dl(self, args):
        """Control DL actuator: dl [on|off]"""
        
        if "DL" not in self.actuators:
            print("[ERROR] DL actuator not available")
            return
        
        if not args:
            print("Usage: dl [on|off]")
            return
        
        action = args[0]

        if action == "on":
            self.actuators["DL"].on()
        elif action == "off":
            self.actuators["DL"].off()
        else:
            print(f"[ERROR] Unknown DL action: {action}")

    
    def cmd_help(self, args):
        """Show available commands."""
        print("\n[PI1] Available commands:")
        print("  exit, quit, e     - Exit the application")
        print("  status            - Show system status")
        print("  db on             - Turn on DB actuator")
        print("  db off            - Turn off DB actuator")
        print("  db beep <seconds> - Beep for specified duration")
        print("  dl on             - Turn on DL actuator")
        print("  dl off            - Turn off DL actuator")
        print("  help              - Show this help message")
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
