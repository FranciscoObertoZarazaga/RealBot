from Config import THREADS
from datetime import datetime
from time import sleep
import pytz


class Tester:
    def __init__(self):
        super(Tester, self).__init__()
        self.last_activity = None
        self.is_runnable = True

    def test_ws(self):
        return THREADS['bot'].is_alive()

    def set_last_activity(self):
        self.last_activity = datetime.now(tz=pytz.timezone('America/Cordoba')).strftime("%H:%M %d-%m-%Y")

    def test(self):
        test_ws = self.test_ws()
        msg = f'State: {"On" if test_ws else "Off"}\nLast update: {self.last_activity}'
        diagnostic = {'test_ws': test_ws, 'last_activity': self.last_activity, 'msg': msg}
        return diagnostic

    def run(self):
        while self.is_runnable:
            sleep(3)
            diagnostic = self.test()

    def restart(self):
        pass


TESTER = Tester()


