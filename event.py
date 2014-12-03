class Event:
    def __init__(self,event_type, **kwargs):
        self.event_type = event_type
        for key in kwargs:
            self.__dict__[key] = kwargs[key]
    def __getitem__(self,key):
        return self.data[key]
