import time
import threading
from ..base.button_interface import ButtonInterface

def loop(button):
  pass

class Button(ButtonInterface):
  def __init__(self, config, stop_event, callback):
     super().__init__(config, stop_event, callback)
     self.log("Initializing real button on pin {}".format(self.config.get('pin', 'N/A')))
  
  def detect_press(self):
    print("Real button not implemented yet")
    pass

  def start(self):
    print("Real button start not implemented yet")
    pass

  def cleanup(self):
    print("Real button cleanup not implemented yet")
    pass

  def read(self):
    print("Real button read not implemented yet")
    pass

  def log(self, message: str) -> None:
    super().log(message)

  def should_stop(self):
    return super().should_stop()