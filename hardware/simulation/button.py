import random
import time
import threading
from ..base.button_interface import ButtonInterface

def loop(button):
  button.log("Button simulation started")
  while not button.should_stop():
    state_change = button.detect_press()
    
    if state_change is not None:
        button.callback(state_change, button.config)
    
    time.sleep(button.config.get('poll_interval', 0.5))

  button.log("Simulation loop stopped")


class Button(ButtonInterface):
  def __init__(self, config, stop_event, callback):
     super().__init__(config, stop_event, callback)
     self.log("Initializing simulated button on pin {}".format(self.config.get('pin', 'N/A')))

  def detect_press(self):
    if random.random() < 0.1:
      new_state = not self.pressed
      self.pressed = new_state
      
      if new_state:
          self.log("Button PRESSED (simulated)")
      else:
          self.log("Button RELEASED (simulated)")
      
      return self.pressed
        
    return None
  
  def start(self):
    """Starts the simulation in a separate thread"""
    thread = threading.Thread(
        target=loop, 
        args=(self,),
        name=f"SimButton-{self.config.get('name', 'unknown')}"
    )
    thread.daemon = True
    thread.start()
    self.log("Thread started")
    return thread
  
  def read(self):
    return self.pressed
  
  def log(self, message: str) -> None:
    super().log(message)

  def should_stop(self):
    return super().should_stop()