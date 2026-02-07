from ..base.db_interface import DBInterface
import time

class DB(DBInterface):

    def __init__(self, config, stop_event, callback):
        super().__init__(config, stop_event, callback)
        self.is_on = False
        self.log(
            "Initializing DB (Door Buzzer) on pin {}".format(
                self.config.get("pin", "N/A")
            )
        )

    def on(self):
        if not self.is_on:
            self.is_on = True
            self.log("BUZZER ON 🔊 (simulated)")
            self.callback(self.config, self.is_on)
        else:
            self.log("BUZZER IS ALREADY ON")

    def off(self):
        if self.is_on:
            self.is_on = False
            self.callback(self.config, self.is_on)
            self.log("BUZZER OFF 🔇 (simulated)")
        else:
            self.log("BUZZER IS ALREADY OFF")

    def beep(self, duration: float):
      self.log(f"BUZZER BEEP for {duration}s (simulated)")
      time.sleep(duration)
