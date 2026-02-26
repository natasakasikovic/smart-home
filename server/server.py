import threading

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json

from server.state import state
from server.mqtt_listener import MQTTListener
from system_orchestrator import SystemOrchestrator
from server.kitchen_timer import KitchenTimerService

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

token = "XDGVPvq5PH0WSV3OSUGrk2jmUt1oQnDxNQ6ngYDdRk7rCDxb9LUf4myDETWCZH0xxCeEs43SS09CpGJOZu-quw=="
org = "FTN"
url = "http://localhost:8086"
bucket = "example_db"
influxdb_client = InfluxDBClient(url=url, token=token, org=org)

tags = ["simulated", "runs_on", "name", "verbose", "code"]

def save_to_db(topic, data):
    """Save sensor/actuator data to InfluxDB"""
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    point = Point(topic)
    
    for key, value in data.items():
        if key in tags:
            point = point.tag(key, value)
        else:
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    point = point.field(f"{key}_{sub_key}", sub_value)
            else:
                point = point.field(key, value)
    
    try:
        write_api.write(bucket=bucket, org=org, record=point)
    except Exception as e:
        print(f"[INFLUX_ERROR] Failed to save {topic}: {e}")



mqtt_listener = MQTTListener(broker="127.0.0.1", port=1883, socketio=socketio) # TODO: extract to env
mqtt_listener.start()
kitchen_timer = KitchenTimerService(mqtt_publish_fn=mqtt_listener.publish)

def influx_callback(client, userdata, msg):
    data = json.loads(msg.payload.decode('utf-8'))
    save_to_db(msg.topic, data)
    parts = msg.topic.split("/")

    if parts[0] == "sensors" and len(parts) > 1:
        code = parts[-1].upper()
        state.update_sensor(code, data.copy())
    elif parts[0] == "actuators" and len(parts) > 1:
        code = parts[-1].upper()
        state.update_actuator(code, data.copy())

def alarm_event_callback(event_type: str, details: dict = None):
    """Save alarm state changes to InfluxDB"""
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    point = Point("alarm_events") \
        .tag("event_type", event_type) \
        .field("active", event_type in ["alarm_triggered", "system_armed"]) \
        .field("details", str(details or {}))
    try:
        write_api.write(bucket=bucket, org=org, record=point)
        print(f"[INFLUX] Alarm event saved: {event_type}")
    except Exception as e:
        print(f"[INFLUX_ERROR] Failed to save alarm event: {e}")

mqtt_listener.client.message_callback_add("sensors/#", influx_callback)
mqtt_listener.client.message_callback_add("actuators/#", influx_callback)

orchestrator = SystemOrchestrator(mqtt_client=mqtt_listener.client, 
                                  state=state, 
                                  socketio=socketio, 
                                  kitchen_timer=kitchen_timer, 
                                  alarm_event_callback=alarm_event_callback)
orchestrator.register()

@app.route('/api/state', methods=['GET'])
def get_state():
    return jsonify(state.get_all())


@app.route('/api/actuator/<code>', methods=['POST'])
def control_actuator(code):
    """
    Body example:
    - DB/DL: {"action": "on"} or {"action": "off"}
    - RGB: {"action": "set_color", "params": {"red": true, "green": false, "blue": true}}
    """
    data = request.json
    action = data.get('action')
    params = data.get('params', {})

    if code == '4SD':
        if action == 'set_timer':
            kitchen_timer.set_timer(params.get('seconds', 0))
        elif action == 'start':
            kitchen_timer.start()
        elif action == 'stop':
            kitchen_timer.stop()
        return jsonify({"status": "ok"})
    
    if code == 'BTN' and action == 'configure':
        kitchen_timer.configure_btn(params.get('add_seconds', 10))
        return jsonify({"status": "ok"})
    
    topic = f"commands/{code.lower()}"
    mqtt_listener.publish(topic, {
        "action": action,
        "params": params
    })
    
    return jsonify({"status": "ok", "actuator": code, "action": action})


@app.route('/api/alarm/arm', methods=['POST'])
def arm_alarm():
    data = request.json
    pin = data.get('pin')
    
    if not state.check_pin(pin):
        return jsonify({"error": "Wrong PIN"}), 401
    
    orchestrator.start_arming()
    
    return jsonify({"status": "arming", "delay": 10})

@app.route('/api/alarm/disarm', methods=['POST'])
def disarm_alarm():
    data = request.json
    pin = data.get('pin')
    
    if state.check_pin(pin):
        orchestrator.disarm()
        return jsonify({"status": "ok"})
    else:
        return jsonify({"error": "Wrong PIN"}), 401
    

@app.route('/api/person_count', methods=['POST'])
def update_person_count():
    data = request.json
    action = data.get('action')
    value = data.get('value', 0)
    
    if action == 'set':
        state.set_person_count(value)
    
    socketio.emit('state', state.get_all())
    
    return jsonify({"status": "ok", "person_count": state.person_count})


@socketio.on('connect')
def handle_connect():
    print("[WS] Client connected")
    socketio.emit('state', state.get_all())


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)