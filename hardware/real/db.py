from ..base.db_interface import DBInterface

def loop(ds):
    pass

class DB(DBInterface):
    def __init__(self, config, stop_event):
        super().__init__(config, stop_event)
        self.log(
            "Initializing REAL DB (Door Buzzer) on pin {}".format(
                self.config.get("pin", "N/A")
            )
        )

    def on(self):
        print("Real DB ON not implemented yet")

    def off(self):
        print("Real DB OFF not implemented yet")

    def beep(self, duration: float):
        print(f"Real DB BEEP for {duration}s not implemented yet")

    def cleanup(self):
        print("Real DB cleanup not implemented yet")
