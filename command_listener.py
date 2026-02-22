import paho.mqtt.client as mqtt
import json

_actuators = {}

def execute_action(actuator, code, action, params):
    """Executes the given action on the actuator based on the code and parameters."""

    # DB & DL 
    if code == "DB" or code == "DL":
        if action == "on":
            actuator.on()
        elif action == "off":
            actuator.off()

    # RGB
    if code == "RGB":
        if action == "white":
            actuator.white()
        elif action == "red":
            actuator.red()
        elif action == "green":
            actuator.green()
        elif action == "blue":
            actuator.blue()
        elif action == "yellow":
            actuator.yellow()
        elif action == "purple":
            actuator.purple()
        elif action == "light_blue":
            actuator.light_blue()
        elif action == "set_color":
            actuator.set_color(
                params.get('red', False),
                params.get('green', False),
                params.get('blue', False)
            )
        elif action == "off":
            actuator.off()
    
    # LCD
    elif code == "LCD":
        if action == "display_text":
            actuator.display_text(params.get('text', ''), params.get('line', 0))
        elif action == "clear":
            actuator.clear()
        elif action == "backlight":
            actuator.change_backlight_state(params.get('state', True))

    # === 4SD (7-Segment Display Timer) ===
    elif code == "4SD":
        if action == "set_timer":
            total_seconds = params.get('seconds', 0)
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            actuator.set_time(minutes, seconds)
        elif action == "start":
            actuator.start_timer()
        elif action == "stop":
            actuator.stop_timer()

    # === BTN (Kitchen Button) ===
    elif code == "BTN":
        if action == "configure":
            add_seconds = params.get('add_seconds', 10)
            actuator.configure_add_seconds(add_seconds)


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode('utf-8'))
    action = payload.get('action')
    params = payload.get('params', {})
    code = topic.split('/')[-1].upper()
    if code not in _actuators:
        return
    
    actuator = _actuators[code]
    print(f"[CMD] {code}: action - {action}")
    
    execute_action(actuator, code, action, params)


def on_connect(client, userdata, flags, rc):
    print(f"[CMD] Connected on MQTT (rc={rc})")
    client.subscribe("commands/#")


def start(actuators, broker="localhost", port=1883):
    global _actuators
    _actuators = actuators
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port, 60)
    client.loop_start()
    
    return client


def stop(client):
    client.loop_stop()
    client.disconnect()