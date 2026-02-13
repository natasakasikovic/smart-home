import threading
from typing import Callable, Dict, Any

class LCDManager:

    @staticmethod
    def create_lcd(
        config: Dict[str, Any],
        stop_event: threading.Event,
        callback: Callable
    ):
        simulate = config.get("simulated", True)

        if simulate:
            print(f"Creating simulated LCD for {config.get('name', 'unknown')}.")
            from hardware.simulation.lcd import LCD
            return LCD(config, stop_event, callback)
        else:
            print(f"Creating real LCD for {config.get('name', 'unknown')}.")
            from hardware.real.lcd.lcd import LCD
            return LCD(config, stop_event, callback)

    @staticmethod
    def start_lcd(
        config: Dict[str, Any],
        stop_event: threading.Event,
        publisher=None
    ) -> threading.Thread:

        def lcd_callback(action_data, cfg):
            payload = {
                "name": cfg.get("name", "unknown"),
                "type": "LCD",
                "action": action_data.get("action", "unknown"),
                "data": action_data,
                "simulated": cfg.get("simulated", True),
                "runs_on": cfg.get("runs_on", "unknown")
            }

            topic = cfg.get("topic", "actuators/lcd")
            publisher.add_measurement(topic, payload)

        lcd = LCDManager.create_lcd(config, stop_event, lcd_callback)

        print(f"[LCD_MANAGER] LCD '{config.get('name', 'unknown')}' started successfully")
        return lcd