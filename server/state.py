import threading
from datetime import datetime

class State:
    def __init__(self):
        self.lock = threading.Lock()
        
        self.alarm_active = False
        self.security_armed = False
        self.pin_code = "1234"
        self.person_count = 0
        
        self.sensors = {}
        self.actuators = {}
    
    def update_sensor(self, code, data):
        with self.lock:
            data['timestamp'] = datetime.now().isoformat()
            
            if code not in self.sensors:
                self.sensors[code] = {}
            
            self.sensors[code].update(data)
    
    def update_actuator(self, code, data):
        with self.lock:
            data['timestamp'] = datetime.now().isoformat()
            
            if code not in self.actuators:
                self.actuators[code] = {}
            
            self.actuators[code].update(data)
    
    def get_all(self):
        # returns a snapshot of the current state
        with self.lock:
            return {
                "alarm_active": self.alarm_active,
                "security_armed": self.security_armed,
                "person_count": self.person_count,
                "sensors": self.sensors.copy(),
                "actuators": self.actuators.copy()
            }
    
    def set_alarm(self, active):
        with self.lock:
            self.alarm_active = active
    
    def set_security(self, armed):
        with self.lock:
            self.security_armed = armed
    
    def check_pin(self, pin):
        with self.lock:
            return self.pin_code == pin

state = State()