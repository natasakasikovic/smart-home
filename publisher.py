import threading
import json
import time
import paho.mqtt.client as mqtt


def publisher_task(publisher, event):
    while not publisher.stop_event.is_set():
        event.wait(timeout=1)

        with publisher.lock:
            if not publisher.batch:
                event.clear()
                continue

            local_batch = publisher.batch.copy()
            publisher.batch.clear()
            publisher.current_size = 0

        event.clear()

        for (topic, payload, qos, retain) in local_batch:
            if publisher._client and publisher._connected:
                publisher._client.publish(topic, payload, qos=qos, retain=retain)


class Publisher:
    def __init__(self, config):
        self.hostname = config['hostname']
        self.port = config['port']
        self.batch_size = config['batch_size'] if 'batch_size' in config else 5
        self.stop_event = threading.Event()
        self.thread = None

        self.batch = []
        self.current_size = 0
        self.lock = threading.Lock()
        self.publish_event = threading.Event()

        self._connected = False
        self._client = None
        self._setup_client()

    def _setup_client(self):
        import uuid
        self._client = mqtt.Client(client_id=f"publisher-{uuid.uuid4().hex[:6]}", clean_session=True)
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._connected = True
            print(f"[PUBLISHER] Connected to MQTT broker at {self.hostname}:{self.port}")
        else:
            self._connected = False
            print(f"[PUBLISHER] Connection failed (rc={rc})")

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        if rc != 0:
            print(f"[PUBLISHER] Unexpected disconnect (rc={rc}), reconnecting...")

    def start_daemon(self):
        try:
            self._client.connect(self.hostname, self.port, keepalive=60)
        except Exception as e:
            print(f"[PUBLISHER] Failed to connect: {e}")

        self._client.loop_start()

        time.sleep(0.5)

        self.thread = threading.Thread(
            target=publisher_task,
            args=(self, self.publish_event),
            daemon=True
        )
        self.thread.start()

    def shutdown(self):
        self.stop_event.set()
        self.publish_event.set()
        if self.thread:
            self.thread.join(timeout=2)
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()

    def add_measurement(self, topic, payload):
        should_publish = False

        with self.lock:
            self.batch.append((topic, json.dumps(payload), 0, False))
            self.current_size += 1
            if self.current_size >= self.batch_size:
                should_publish = True
        if should_publish:
            self.publish_event.set()