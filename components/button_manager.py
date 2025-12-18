import threading
from typing import Callable, Dict, Any

class ButtonManager:

  @staticmethod
  def create_button(config: Dict[str, Any], stop_event: threading.Event, callback: Callable) -> 'ButtonManager':
      simulate = config.get("simulated", True)

      if simulate:
        print(f"Creating simulated button for {config.get('name', 'unknown')}.")
        from hardware.simulation.button import Button
        return Button(config, stop_event, callback)
      else:
        print(f"Creating real button for {config.get('name', 'unknown')}.")
        from hardware.real.button import Button
        return Button(config, stop_event, callback)
      
  @staticmethod
  def start_button(config: Dict[str, Any], stop_event: threading.Event, publisher=None) -> threading.Thread:
      def button_callback(state, cfg):
          payload = {
              "name": cfg.get("name", "unknown"),
              "type": "button",
              "state": state
          }
          
          if publisher: # TODO: implement publisher
                publisher.add_measurement("Button", payload)

      button = ButtonManager.create_button(config, stop_event, button_callback)
      thread = button.start()

      print(f"[BUTTON_MANAGERA] Button '{config.get('name', 'unknown')}' started successfully")
      return thread

  