class CommandHandler:
    """Handles user commands for the PI2 system"""
    
    def __init__(self, actuators, threads, stop_event):
        self.actuators = actuators
        self.threads = threads
        self.stop_event = stop_event
        self.commands = {
            'exit': self.cmd_exit,
            'e': self.cmd_exit,
            'quit': self.cmd_exit,
            'status': self.cmd_status,
            'ssd': self.cmd_ssd,
            'help': self.cmd_help,
        }
    
    def cmd_exit(self, args):
        print("[PI2] Shutting down...")
        self.stop_event.set()
    
    def cmd_status(self, args):
        active = len([t for t in self.threads if t.is_alive()])
        print(f"[PI2] Active threads: {active}")
        print(f"[PI2] Active actuators: {list(self.actuators.keys())}")
    
    def cmd_ssd(self, args):
        """Control 7-segment display actuator: ssd [display <value>|clear]"""
        if "4SD" not in self.actuators:
            print("[ERROR] SSD actuator not available")
            return
        
        if not args:
            print("Usage: ssd [display <value>|clear]")
            return
        
        action = args[0].lower()
        
        if action == "display":
            if len(args) < 2:
                print("Usage: ssd display <value>")
                return
            value = args[1]
            self.actuators["4SD"].display_time(value)
        elif action == "clear":
            self.actuators["4SD"].clear()
        else:
            print(f"[ERROR] Unknown SSD action: {action}")
    
    def cmd_help(self, args):
        print("\n[PI2] Available commands:")
        print("  exit, quit, e          - Exit the application")
        print("  status                 - Show system status")
        print("  ssd display <value>    - Display 4-digit value on SSD")
        print("  ssd clear              - Clear the SSD display")
        print("  help                   - Show this help message\n")
    
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