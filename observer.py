class Observer:
    def __init__(self):
        self.messages = []

    def send(self,message):
        self.messages.append(message)

    def handle(self,message):
        pass

    def handle_all(self):
        while len(self.messages):
            self.handle(message)
            while message in self.messages():
                self.messages.remove(message)
