import threading
import json

class SystemOrchestrator:
    """
    Handles automation rules by listening to sensor MQTT topics
    and publishing commands to commands/* topics
    """
    
    def __init__(self, mqtt_client, state, socketio=None):
        self.mqtt_client = mqtt_client
        self.state = state
        self.socketio = socketio
        self._lock = threading.Lock()
        
        self._dl_timer = None
        self._door_alarm_timers = {}
    
    def register(self):
        """Registration of all automation rules"""
        self.mqtt_client.message_callback_add("sensors/dpir1", self._on_dpir1)
        # TODO: add all rules    
  
    def _on_dpir1(self, client, userdata, msg):
        """When DPIR1 detects motion, turn DL on for 10 seconds"""
        payload = json.loads(msg.payload.decode())
        motion_detected = payload.get("detected", False)
        
        print(f"[ORCH] DPIR1 motion: {motion_detected}")
        
        if not motion_detected:
            return
        
        self._activate_dl(duration=10)
    
    def _activate_dl(self, duration=10):
        """Turn DL on, then off after duration seconds"""
        
        with self._lock:
            if self._dl_timer:
                self._dl_timer.cancel()
        
        self._publish_command("dl", "on")
        
        timer = threading.Timer(duration, self._deactivate_dl)
        timer.daemon = True
        timer.start()
        
        with self._lock:
            self._dl_timer = timer
    
    def _deactivate_dl(self):
        """Turn DL off"""
        self._publish_command("dl", "off")
    
 
    def _publish_command(self, device_code: str, action: str, params: dict = None):
        """Publish command to MQTT commands/* topic"""
        topic = f"commands/{device_code.lower()}"
        payload = {"action": action, "params": params or {}}
        
        self.mqtt_client.publish(topic, json.dumps(payload))
        print(f"[ORCH] → {topic}: {payload}")