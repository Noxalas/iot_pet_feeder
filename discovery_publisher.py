import os
import json

from config import *

ENTITY_TYPES = [
    "sensor",
    "number",
    "input_number",
    "switch",
    "button",
    "binary_sensor",
    "text",
    "select"
]

class DiscoveryPublisher:
    def __init__(self, mqtt_client):
        self.mqtt = mqtt_client


    def get_discovery_topic_from_filename(self, filename):
        basename = os.path.splitext(filename)[0]
        for entity_type in ENTITY_TYPES:
            if basename.startswith(entity_type + "_"):
                rest = basename[len(entity_type) + 1:]
                try:
                    device, object_id = rest.split("_", 1)
                except ValueError:
                    print(f"Skipping filename: {filename}")
                    return None

                return f"{DISCOVERY_PREFIX}/{entity_type}/{device}/{object_id}/config"

        print(f"Unsupported entity type in filename: {filename}")
        return None


    def publish_configs(self):
        for filename in os.listdir(DISCOVERY_CONFIG_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(DISCOVERY_CONFIG_DIR, filename)
                with open(filepath, "r") as f:
                    try:
                        payload = json.load(f)
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse {filename}: {e}")
                        continue
                
                topic = self.get_discovery_topic_from_filename(filename)

                if topic:
                    self.mqtt.publish(topic, json.dumps(payload), retain=True)
                    print(f"Published {filename} -> {topic}")