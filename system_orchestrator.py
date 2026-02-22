import threading, json, time
from collections import defaultdict, deque


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

        self.dus_history = defaultdict(lambda: deque(maxlen=20))
    
    def register(self):
        """Registration of all automation rules"""
        self.mqtt_client.message_callback_add("sensors/dpir", self._on_dpir) 
        self.mqtt_client.message_callback_add("sensors/ds1", self._on_ds)
        self.mqtt_client.message_callback_add("sensors/gsg", self._on_gsg) 
        self.mqtt_client.message_callback_add("sensors/dus",self._on_dus)
        # TODO: add all rules    

  
    def _on_dpir(self, client, userdata, msg):
        """When DPIR1 detects motion, turn DL on for 10 seconds.
           When DPIR1 or DPIR2 detect motion, determine wheather person is entering or exiting.
           """
        payload = json.loads(msg.payload.decode())
        runs_on = payload.get("runs_on")

        if runs_on == "PI1":
            self._activate_dl(duration=10)

        person_count = self.state.person_count

        if self._is_entering(runs_on):
            person_count += 1
        else:
            person_count -= 1

        self.state.set_person_count(person_count)


    def _on_dus(self, client, userdata, msg):
        """ HELPER -> Processes DUS messages and stores recent distance data per device for enter/exit detection."""
        payload = json.loads(msg.payload.decode())

        distance = payload.get("distance_cm")
        runs_on = payload.get("runs_on")

        if distance is None or runs_on is None:
            return

        self.dus_history[runs_on].append({
            "distance": distance,
            "time": time.time()
        })

    def _on_gsg(self, client, userdata, msg):
        """When gyroscope detects significant change, turn on alarm"""
        self._trigger_alarm(True) # TODO: think about moving logic about significant change here

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

    
    def _is_entering(self, runs_on: str, window_seconds: float = 3.0) -> bool:
        """ Returns True if movement trend indicates someone is entering."""
        return self._detect_direction(runs_on, window_seconds) == "enter"

    def _detect_direction(self, runs_on: str, window_seconds: float = 3.0):
        """ Determines movement direction (enter/exit) based on DUS distance history.
            Returns: "enter", "exit", or None if unclear
        """
        now = time.time()
        history = [x for x in self.dus_history[runs_on] if now - x["time"] <= window_seconds]

        if len(history) < 2:
            return None

        delta = history[0]["distance"] - history[-1]["distance"]

        if delta > 5:
            return "enter"
        elif delta < -5:
            return "exit"
        else:
            return None
    
    def _publish_command(self, device_code: str, action: str, params: dict = None):
        """Publish command to MQTT commands/* topic"""
        topic = f"commands/{device_code.lower()}"
        payload = {"action": action, "params": params or {}}
        
        self.mqtt_client.publish(topic, json.dumps(payload))
        print(f"[ORCH] → {topic}: {payload}")