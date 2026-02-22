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
        self._lock = threading.RLock()
        
        self._dl_timer = None

        self._ds_timers = {}
        self._open_doors = set()

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
           If the number of people inside the building is zero, detecting motion on any of the DPIR1–3 sensors triggers the alarm.
           """
        payload = json.loads(msg.payload.decode())
        runs_on = payload.get("runs_on")

        if runs_on == "PI1":
            self._activate_dl(duration=10)
        
        direction = self._detect_direction(runs_on)

        if direction is None:
            return

        with self._lock:

            person_count = self.state.person_count

            if person_count == 0:
                print("Zero people inside smart home + motion detected -> ALARM ON")
                self._trigger_alarm()

            if direction == "enter":
                person_count += 1
                print(f"Somebody entered in smart home. Person count: {person_count}")
            elif direction == "exit" and person_count > 0:
                person_count -= 1
                print(f"Somebody exited from smart home. Person count: {person_count}")

            self.state.set_person_count(person_count)


    def _on_dus(self, client, userdata, msg):
        """ HELPER -> Processes DUS messages and stores recent distance data per device for enter/exit detection."""
        payload = json.loads(msg.payload.decode())

        distance = payload.get("distance")
        runs_on = payload.get("runs_on")

        if distance is None or runs_on is None:
            return

        self.dus_history[runs_on].append({
            "distance": distance,
            "time": time.time()
        })

    def _on_gsg(self, client, userdata, msg):
        """When gyroscope detects significant change, turn on alarm"""
        print("Gyroscope detected significant change -> Alarm ON")
        self._trigger_alarm() # TODO: think about moving logic about significant change here

    def _on_ds(self, client, userdata, msg):
        """Handle DS sensors on ds1 topic, using runs_on to differentiate"""
        
        payload = json.loads(msg.payload.decode())
        state = payload.get("state", "CLOSED")
        runs_on = payload.get("runs_on")

        if not runs_on:
            return

        with self._lock:
            if state == "OPEN":
                self._open_doors.add(runs_on)

                if runs_on in self._ds_timers:
                    self._ds_timers[runs_on].cancel()

                timer = threading.Timer(5, lambda: self._check_and_trigger(runs_on))
                timer.start()
                self._ds_timers[runs_on] = timer

            else:
                if runs_on in self._ds_timers:
                    self._ds_timers[runs_on].cancel()
                    del self._ds_timers[runs_on]

                self._open_doors.discard(runs_on)

                if not self._open_doors and self.state.alarm_active:
                    self.state.set_security(False)
                    self.state.set_alarm(False)

    def _check_and_trigger(self, runs_on):
        with self._lock:
            if runs_on in self._open_doors:
                self._trigger_alarm()

    def _trigger_alarm(self):
        with self._lock:
            print(f"Alarm ON")
            self.state.set_security(True)
            self.state.set_alarm(True)
    
    def _activate_dl(self, duration=10):
        """Turn DL on, then off after duration seconds"""
        
        with self._lock:
            if self._dl_timer:
                self._dl_timer.cancel()
        
        self._publish_command("dl", "on")
        
        timer = threading.Timer(duration, lambda: self._publish_command("dl", "off")) # turn off dl
        timer.daemon = True
        timer.start()
        
        with self._lock:
            self._dl_timer = timer
    
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