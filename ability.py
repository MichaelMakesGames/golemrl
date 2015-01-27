from config import *

from event import Event
from observer import Observer, Subject

class Ability(Observer,Subject):
    def __init__(self, game, ability_id,
                 name,
                 trigger, effect,
                 message=None):
        Subject.__init__(self)
        self.game = game
        self.ability_id = ability_id
        self.name = name
        self.message = message
        self.trigger = trigger
        self.effect = effect

    def on_notify(self,event):
        if self.trigger(self.game,self,event):
            self.notify(Event(EVENT_RESOLVE_ABILITY,
                              ability=self,
                              event=self.effect(self.game,self,event)))
