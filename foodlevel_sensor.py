import RPi.GPIO as GPIO
import time
import statistics
from config import *

class FoodLevelSensor:
    def __init__(self, mqtt_client, trigger_pin=25, echo_pin=24, number_of_samples=5, calibration_distance_cm=30, calibration_echo_us=1750, sample_sleep=0.01, timeout=1.0):
        print("Setting up food level sensor...")
        self.mqtt = mqtt_client
        
        self.trigger_pin = trigger_pin # output GPIO
        self.echo_pin = echo_pin # input GPIO
        self.number_of_samples = number_of_samples # number of times to test distance
        self.calibration_distance_cm = calibration_distance_cm # calibration distance
        self.calibration_echo_us = calibration_echo_us # median value reported by sensor at 30 cm
        self.sample_sleep = sample_sleep # amount of time between sample requests
        self.timeout = timeout # time in seconds in which the program is considered stuck

        self.samples = []
        self.stack = []
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(trigger_pin, GPIO.OUT)
        GPIO.setup(echo_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        GPIO.add_event_detect(echo_pin, GPIO.BOTH, callback=self._timer_callback)
        print("Sensor set up!")


    ## callback when rising edge is detected on echo pin
    def _timer_callback(self, channel):
        now = time.monotonic()
        self.stack.append(now)


    def _trigger(self):
        GPIO.output(self.trigger_pin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, GPIO.LOW)


    def read_distance_cm(self):
        self.samples.clear()

        while len(self.samples) < self.number_of_samples:
            self._trigger()

            start = time.monotonic()
            while len(self.stack) < 2 and (time.monotonic() - start) < self.timeout:
                pass
            
            if len(self.stack) == 2:
                duration = self.stack.pop() - self.stack.pop()
                self.samples.append(duration)
            elif len(self.stack) > 2:
                self.stack.clear()
            
            time.sleep(self.sample_sleep)
        
        median_duration = statistics.median(self.samples)

        distance_cm = (median_duration * 1_000_000) * self.calibration_distance_cm / self.calibration_echo_us
        return round(distance_cm, 2)
    

    def read_food_level(self):
        max_distance = FOOD_CONTAINER_HEIGHT
        min_distance = 2

        distance_cm = self.read_distance_cm()
        distance_cm = max(min_distance, min(distance_cm, max_distance))

        percentage = 100 * (max_distance - distance_cm) / (max_distance - min_distance)
        percentage = max(0, min(percentage, 100))
        return round(percentage, 1)


    def publish_food_level(self, level: float = None):
        if level == None:
            level = self.read_food_level()
            
        if self.mqtt:
            self.mqtt.publish(TOPIC_STATUS + "foodlevel", str(level), retain=True)
        else:
            print(f"Cannot publish food level! (Current food level:{level})")


    def cleanup(self):
        GPIO.cleanup([self.trigger_pin, self.echo_pin])

