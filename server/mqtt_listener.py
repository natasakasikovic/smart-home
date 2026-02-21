import paho.mqtt.client as mqtt
import json
from server.state import state

class MQTTListener:
    def __init__(self, broker="localhost", port=1883, socketio=None):
        self.broker = broker
        self.port = port
        self.socketio = socketio
        self.client = mqtt.Client()
        
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
    
    def _on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT_LISTENER] connected (rc={rc})")
        client.subscribe("sensors/#")
        client.subscribe("actuators/#")
    
    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = json.loads(msg.payload.decode('utf-8'))
        
        parts = topic.split('/')
        if len(parts) < 2:
            return
        
        category = parts[0]
        code = parts[1].upper()
        
        if category == "sensors":
            state.update_sensor(code, payload)
        elif category == "actuators":
            state.update_actuator(code, payload)
        
        if self.socketio:
            self.socketio.emit('update', {'topic': topic, 'data': payload})
    
    def start(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()
    
    def publish(self, topic, data):
        self.client.publish(topic, json.dumps(data))