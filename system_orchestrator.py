import threading, json, time
from collections import defaultdict, deque


class SystemOrchestrator:
    """
    Handles automation rules by listening to sensor MQTT topics
    and publishing commands to commands/* topics
    """
    
    def __init__(self, mqtt_client, state, socketio=None, kitchen_timer=None, alarm_event_callback=None):
        self.mqtt_client = mqtt_client
        self.state = state
        self.socketio = socketio
        self.kitchen_timer = kitchen_timer
        self._alarm_event_callback = alarm_event_callback
        self._lock = threading.RLock()
        
        self._dl_timer = None

        self._ds_timers = {}
        self._open_doors = set()

        self._arm_timer = None
        self._grace_timer = None

        self.dus_history = defaultdict(lambda: deque(maxlen=20))

        self._lcd_index = 0
        self._lcd_interval = 2
        self._lcd_thread = None
        self._dht_values = {} 
        self._lcd_sensors = ["DHT1", "DHT2", "DHT3"] 
        for sensor in self._lcd_sensors:
            self._dht_values[sensor] = {"temperature": None, "humidity": None}  
     
    def register(self):
        """Registration of all automation rules"""
        self.mqtt_client.message_callback_add("sensors/dpir", self._on_dpir) 
        self.mqtt_client.message_callback_add("sensors/ds1", self._on_ds)
        self.mqtt_client.message_callback_add("sensors/gsg", self._on_gsg) 
        self.mqtt_client.message_callback_add("sensors/dus", self._on_dus)
        self.mqtt_client.message_callback_add("sensors/dms", self._on_dms)
        self.mqtt_client.message_callback_add("sensors/dht", self._on_dht)
        self.mqtt_client.message_callback_add("actuators/btn", self._on_btn)
        self.mqtt_client.message_callback_add("sensors/ir", self.handle_ir)

        self._start_lcd_cycle()

    def start_arming(self):
        """Called from web app to arm the system via UI (same as DMS PIN entry)"""
        with self._lock:
            if self._arm_timer:
                self._arm_timer.cancel()
            self._arm_timer = threading.Timer(10, self._arm_system)
            self._arm_timer.daemon = True
            self._arm_timer.start()
            if self.socketio:
                self.socketio.emit('arming', {'countdown': 10})

    def disarm(self):
        """Called from web app to disarm"""
        with self._lock:
            if self._grace_timer:
                self._grace_timer.cancel()
                self._grace_timer = None
            if self._arm_timer:
                self._arm_timer.cancel()
                self._arm_timer = None
            self.state.set_security(False)
            self.state.set_alarm(False)
            self._publish_command("db", "off")
            if self._alarm_event_callback:
                self._alarm_event_callback("alarm_disarmed")
            if self.socketio:
                self.socketio.emit('state', self.state.get_all())

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
            if self.socketio:
                self.socketio.emit('state', self.state.get_all())

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

    def _on_dht(self, client, userdata, msg):
        """ Saves newest temperature and humidity for each pi"""
        
        payload = json.loads(msg.payload.decode())
        code = payload.get("code")
        
        if not code:
            return

        with self._lock:
            if code not in self._dht_values:
                self._dht_values[code] = {"temperature": None, "humidity": None}

            self._dht_values[code]["temperature"] = payload.get("temperature")
            self._dht_values[code]["humidity"] = payload.get("humidity")

    def _on_gsg(self, client, userdata, msg):
        """When gyroscope detects significant change, turn on alarm"""
        print("Gyroscope detected significant change -> Alarm ON")
        self._trigger_alarm()

    def _on_ds(self, client, userdata, msg):
        """Handle DS sensors, using runs_on to differentiate between DS1 and DS2"""
        
        payload = json.loads(msg.payload.decode())
        state = payload.get("state", "CLOSED")
        runs_on = payload.get("runs_on")

        if not runs_on:
            return

        with self._lock:
            if state == "OPEN":
                self._open_doors.add(runs_on)

                if self.state.security_armed and not self.state.alarm_active:
                    # 4b - system is armed, give 3s for PIN entry before triggering alarm
                    print(f"[DS] '{runs_on}' is OPEN + system ARMED -> waiting 3s for PIN")
                    if self._grace_timer:
                        self._grace_timer.cancel()
                    self._grace_timer = threading.Timer(3, self._grace_period_expired)
                    self._grace_timer.daemon = True
                    self._grace_timer.start()
                else:
                    # 3 - door open for more than 5s triggers alarm
                    print(f"[DS] '{runs_on}' is OPEN - starting 5s timer. Open doors: {self._open_doors}")

                    if runs_on in self._ds_timers:
                        self._ds_timers[runs_on].cancel()
                        print(f"[DS] '{runs_on}' existing timer cancelled and restarted")

                    timer = threading.Timer(5, lambda: self._check_and_trigger(runs_on))
                    timer.start()
                    self._ds_timers[runs_on] = timer

            else:
                print(f"[DS] '{runs_on}' is CLOSED")

                if runs_on in self._ds_timers:
                    self._ds_timers[runs_on].cancel()
                    del self._ds_timers[runs_on]
                    print(f"[DS] '{runs_on}' timer cancelled - door closed before 5s, alarm will not trigger")

                self._open_doors.discard(runs_on)

                if not self._open_doors and self.state.alarm_active and not self.state.security_armed:
                    print(f"[DS] All doors closed and alarm was active - DEACTIVATING ALARM")
                    self.state.set_security(False)
                    self.state.set_alarm(False)
                    self._publish_command("db", "off")
                    if self.socketio:
                        self.socketio.emit('state', self.state.get_all())

    def _on_dms(self, client, userdata, msg):
        """DMS listens for PIN code entries. If the correct PIN is entered while the alarm is active, it disarms the system."""

        payload = json.loads(msg.payload.decode())
        pin = payload.get("pin")
        
        if pin is None:
            return
        
        with self._lock:
            if self.state.check_pin(str(pin)):
                if self.state.alarm_active or self.state.security_armed:
                    # 4c - correct PIN while alarm is active or system is armed -> DISARM
                    print("[DMS] Correct PIN -> DISARM")
                    if self._grace_timer:
                        self._grace_timer.cancel()
                        self._grace_timer = None
                    if self._arm_timer:
                        self._arm_timer.cancel()
                        self._arm_timer = None
                    self.state.set_security(False)
                    self.state.set_alarm(False)
                    self._publish_command("db", "off")
                    if self._alarm_event_callback:
                        self._alarm_event_callback("alarm_disarmed")
                    if self.socketio:
                        self.socketio.emit('state', self.state.get_all())
                else:
                    # 4a - system is disarmed, correct PIN -> arm after 10s
                    print("[DMS] Correct PIN -> arming in 10s")
                    if self._arm_timer:
                        self._arm_timer.cancel()
                    self._arm_timer = threading.Timer(10, self._arm_system)
                    self._arm_timer.daemon = True
                    self._arm_timer.start()
                    if self.socketio:
                        self.socketio.emit('arming', {'countdown': 10})
            else:
                print("[DMS] Wrong PIN")

    def _on_btn(self, client, userdata, msg):
        payload = json.loads(msg.payload.decode())
        turned_on = payload.get("turned_on")
        
        if turned_on and self.kitchen_timer:
            self.kitchen_timer.on_btn_press()

    def handle_ir(self, client, userdata, msg):
        import json
        data = json.loads(msg.payload.decode('utf-8'))
        key = data.get('key')
        
        IR_TO_RGB = {
            "1": "red",
            "2": "green",
            "3": "blue",
            "4": "yellow",
            "5": "purple",
            "6": "light_blue",
            "7": "white",
            "0": "off",
            "OK": "white",
            "*": "off",
            "#": "off",
        }
        
        action = IR_TO_RGB.get(key)
        if action:
            self.mqtt_client.publish("commands/rgb", json.dumps({
                "action": action,
                "params": {}
            }))
            print(f"[IR] Key '{key}' → RGB '{action}'")
        else:
            print(f"[IR] Unmapped key: '{key}'")

    def _arm_system(self):
        """Arms the system after 10s delay when correct PIN is entered while system is disarmed."""
        with self._lock:
            self._arm_timer = None
            self.state.set_security(True)
            self.state.set_alarm(False)
            print("[ORCH] System ARMED")
            if self._alarm_event_callback:
                self._alarm_event_callback("system_armed")
            if self.socketio:
                self.socketio.emit('state', self.state.get_all())

    def _check_and_trigger(self, runs_on):
        """Point 3 - door open for more than 5s triggers alarm"""
        with self._lock:
            if runs_on in self._open_doors:
                print(f"[DS] '{runs_on}' open >5s - ALARM ON")
                self._trigger_alarm()

    def _grace_period_expired(self):
        """4b - no PIN entered within 3s of door opening while armed -> trigger alarm"""
        with self._lock:
            self._grace_timer = None
            print("[GRACE] Period expired - ALARM ON")
            self._trigger_alarm()

    def _trigger_alarm(self):
        with self._lock:
            print(f"Alarm ON")
            self.state.set_security(True)
            self.state.set_alarm(True)
            self._publish_command("db", "on")
            if self._alarm_event_callback:
                self._alarm_event_callback("alarm_triggered")
            if self.socketio:
                self.socketio.emit('state', self.state.get_all())

    def _start_lcd_cycle(self):
        def lcd_cycle():
            while True:
                with self._lock:
                    sensor = self._lcd_sensors[self._lcd_index % len(self._lcd_sensors)]
                    data = self._dht_values.get(sensor)

                    temperature = data["temperature"]
                    humidity = data["humidity"]

                self._publish_command("lcd", "display_both", {
                    "line0": f"{sensor} Temp: {temperature}",
                    "line1": f"{sensor} Hum: {humidity}"
                })

                self._lcd_index += 1
                time.sleep(self._lcd_interval)

        self._lcd_thread = threading.Thread(target=lcd_cycle, daemon=True)
        self._lcd_thread.start()
    
    def _activate_dl(self, duration=10):
        """Turn DL on, then off after duration seconds"""
        
        with self._lock:
            if self._dl_timer:
                self._dl_timer.cancel()
        
        self._publish_command("dl", "on")
        
        timer = threading.Timer(duration, lambda: self._publish_command("dl", "off"))
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