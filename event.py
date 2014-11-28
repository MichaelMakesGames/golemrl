class Event:
    def __init__(self,event_type, **kwargs):
        self.event_type = event_type
        self.data = kwargs
    def __getitem__(self,key):
        return self.data[key]
