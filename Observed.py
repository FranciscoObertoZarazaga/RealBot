class Observed:
    def __init__(self):
        self.observers = list()

    def subscribe(self,observer):
        if not isinstance(observer,list):
            observer = [observer]
        for obs in observer:
            self.observers.append(obs)

    def notify(self,data):
        for observer in self.observers: observer.update(data)