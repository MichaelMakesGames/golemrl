from config import *

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
        if event.event_type != EVENT_NONE:
            for observer in self.observers:
                observer.on_notify(event)
