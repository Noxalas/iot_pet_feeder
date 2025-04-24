import time
import threading

class FoodLevelPublisher:
    def __init__(self, sensor, interval=300, threshold=1.0):
        self.sensor = sensor
        self.interval = interval # seconds
        self.threshold = threshold
        self._last_level = None
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._loop)
    

    def start(self):
        self._thread.start()
    

    def stop(self):
        self._stop_event.set()
        self._thread.join()
    

    def _loop(self):
        while not self._stop_event.is_set():
            self.publish_if_needed(force=True)
            time.sleep(self.interval)
    

    def publish_if_needed(self, force=False):
        level = self.sensor.read_food_level()
        if force or self._last_level is None or abs(level - self._last_level) >= self.threshold:
            self.sensor.publish_food_level(level)
            self._last_level = level
