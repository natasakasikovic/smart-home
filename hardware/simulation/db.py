from ..base.db_interface import DBInterface
import time

class DB(DBInterface):

    def __init__(self, config, stop_event):
        super().__init__(config, stop_event)
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

    def off(self):
        if self.is_on:
            self.is_on = False
            self.log("BUZZER OFF 🔇 (simulated)")

    def beep(self, duration: float):
      self.log(f"BUZZER BEEP for {duration}s (simulated)")
      time.sleep(duration)
