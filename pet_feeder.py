import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

from config import *

from food_dispenser import *
from foodlevel_sensor import *
from foodlevel_publish import *
from discovery_publisher import *

def _on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(TOPIC_COMMAND + "#") # the '#' wildcard matches any topic under TOPIC_COMMAND

    client.publish(TOPIC_STATUS + "status", "Ready")


def _on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    print(f"Received command: {topic} -> {payload}") 
    
    if topic == "command/petfeeder/dispenser":
        if payload == "feed":
            if not motor.is_busy:
                motor.dispense_food()
                publisher.publish_if_needed(force=True)
    
    elif topic == "command/petfeeder/dispenser/portion":
        try:
            grams = int(payload)
            if grams >= PORTION_MIN and grams <= PORTION_MAX:
                motor.set_portion(grams)
        except ValueError:
            print(f"Invalid portion value: {payload}")
    
    elif topic == "command/petfeeder/status":
        publisher.publish_if_needed(force=True)
    
    else:
        print(f"Unknown command topic, {topic}, with payload, {payload}")


client = mqtt.Client()

discovery_publisher = DiscoveryPublisher(client)

motor = FoodDispenserMotor(client)
sensor = FoodLevelSensor(client)

publisher = FoodLevelPublisher(sensor, 300, 0.5)
publisher.start()

if MQTT_USER and MQTT_PASS:
    client.username_pw_set(MQTT_USER, MQTT_PASS)

client.on_connect = _on_connect
client.on_message = _on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

discovery_publisher.publish_configs()

client.loop_forever()
