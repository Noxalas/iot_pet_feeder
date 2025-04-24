import sys
from time import sleep
from gpiozero import OutputDevice
from config import *

DISPENSING_STEPS = 90

class FoodDispenserMotor:
  def __init__(self, mqtt_client, portion_size=PORTION_DEFAULT):
    print("Setting up food dispenser...")

    self.mqtt = mqtt_client

    self._is_busy = False

    self.portion_size = portion_size

    self.IN1 = OutputDevice(14)
    self.IN2 = OutputDevice(15)
    self.IN3 = OutputDevice(18)
    self.IN4 = OutputDevice(23)

    self.step_sequence = [
      [1,0,0,0],
      [1,1,0,0],
      [0,1,0,0],
      [0,1,1,0],
      [0,0,1,0],
      [0,0,1,1],
      [0,0,0,1],
      [1,0,0,1]
    ]

    print("Food dispenser initialized.")


  @property
  def is_busy(self):
    return self._is_busy
  
  @is_busy.setter
  def is_busy(self, value: bool):
    if value == self._is_busy: return

    self._is_busy = value
    status = "Busy" if value else "Ready"
    self.mqtt.publish(TOPIC_STATUS + "status", str(status), retain=True)
    print(f"Motor status set to: \"{status}\"")


  def set_portion(self, value: float):
    if value == self.portion_size: return

    self.portion_size = value
    print(f"Set new portion size to: {self.portion_size}")


  def set_step(self, w1, w2, w3, w4):
    self.IN1.value = w1
    self.IN2.value = w2
    self.IN3.value = w3
    self.IN4.value = w4
  

  def cleanup(self):
    self.set_step(0, 0, 0, 0)
    print("Motor cleaning up...")


  def step_motor(self, steps, direction=1, delay=0.003):
    print("Running motor ", int(steps), " steps to the ", ("right" if direction == 1 else "left"), " with a ", int(delay), " delay.")
    for _ in range(steps):
      for step in (self.step_sequence if direction > 0 else reversed(self.step_sequence)):
        self.set_step(*step)
        sleep(delay)
    print("Motor finished running.")

    self.cleanup()
  

  def dispense_food(self):
    if self.is_busy: 
      print("Motor is busy. Returning.")
      return

    self.is_busy = True
    self.step_motor(DISPENSING_STEPS, -1)
    
    # assuming 10g/s
    time_to_sleep = max(1.0, self.portion_size / 10.0) 
    sleep(time_to_sleep)
    
    self.step_motor(DISPENSING_STEPS, 1)
    self.is_busy = False
    
