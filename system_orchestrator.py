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

        self._ds_timers = {}
        self._active_doors = set()

    
    def register(self):
        """Registration of all automation rules"""
        self.mqtt_client.message_callback_add("sensors/dpir1", self._on_dpir1) # when DPIR1 detects motion
        self.mqtt_client.message_callback_add("sensors/ds1", self._on_ds) # When DS state changes (on topic sensors/ds1 will )
        # TODO: add all rules    
  
    def _on_dpir1(self, client, userdata, msg):
        """When DPIR1 detects motion, turn DL on for 10 seconds"""
        payload = json.loads(msg.payload.decode())
        motion_detected = payload.get("detected", False)
        
        print(f"[ORCH] DPIR1 motion: {motion_detected}")
        
        if not motion_detected:
            return
        
        self._activate_dl(duration=10)

    def _on_ds(self, client, userdata, msg):
        """Handle DS sensors on ds1 topik, using runs_on to differentiate"""
        payload = json.loads(msg.payload.decode())
        state = payload.get("state", "CLOSED")
        sensor = payload.get("runs_on")  # PI1 or PI2

        if not sensor:
            return 

        with self._lock:
            if state == "OPEN":
                self._active_doors.add(sensor)

                if sensor in self._ds_timers:
                    self._ds_timers[sensor].cancel()

                timer = threading.Timer(5, lambda: self._trigger_alarm(sensor))
                timer.start()
                self._ds_timers[sensor] = timer

            else:  # CLOSED
                if sensor in self._ds_timers:
                    self._ds_timers[sensor].cancel()
                    del self._ds_timers[sensor]

                self._active_doors.discard(sensor)

                if not self._active_doors and self.state.alarm_active:
                    self.state.set_security(False)
                    self.state.set_alarm(False)

    def _trigger_alarm(self, sensor):
        with self._lock:
            if sensor in self._active_doors:
                print(f"Alarm ON")
                self.state.set_security(True)
                self.state.set_alarm(True)
    
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