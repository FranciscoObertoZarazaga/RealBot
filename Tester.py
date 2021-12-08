from Config import THREADS
from Binance import WS
import threading
from datetime import datetime
from time import sleep
from Observed import Observed

class Tester(Observed):
    def __init__(self):
        super(Tester, self).__init__()
        self.last_activity = None
        self.is_runnable = True

    def test_threads(self):
        for thread in THREADS.values():
            if not thread.is_alive():
                return False
        return True

    def set_last_activity(self):
        self.last_activity = datetime.now().strftime("%H:%M %d-%m-%Y")

    def test(self):
        test_threads = self.test_threads()
        msg = f'State: {"On" if test_threads else "Off"}\nLast update: {self.last_activity}'
        diagnostic = {'test_threads':test_threads, 'last_activity':self.last_activity, 'msg':msg}
        return diagnostic

    def run(self):
        while self.is_runnable:
            sleep(3)
            diagnostic = self.test()
            self.notify(diagnostic)

    def restart(self):
        pass


TESTER = Tester()


