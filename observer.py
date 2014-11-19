class Observer:
    def on_notify(self,event):
        pass
    
class Subject:
    def __init__(self):
        self.observers = []
    def add_observer(self,observer):
        if observer not in self.observers:
            self.observers.append(observer)
    def remove_observer(self,observer):
        if observer in self.observers:
            self.observers.remove(observer)
    def notify(self,event):
        for observer in self.observers:
            observer.on_notify(event)
