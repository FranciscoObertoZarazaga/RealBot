import threading

class Tester:
    def __init__(self):
        self.last_activity = None

    def getThreadState(self):
        for thread in threading.enumerate():
            if not thread.is_alive():
                return 'Off'
        return 'On'

    def setLastActivity(self, last_activity):
        self.last_activity = last_activity

    def test(self):
        diagnostic = f'State: {self.getThreadState()}\n'
        diagnostic += f'Last update: {self.last_activity}'
        return diagnostic

    def update(self, msg):
        self.setLastActivity(msg)


TESTER = Tester()


