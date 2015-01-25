from config import *

from event import Event
from observer import Observer

class Ability(Observer):
    def __init__(self, game, ability_id,
                 name,
                 trigger, effect):
        self.game = game
        self.ability_id = ability_id
        self.name = name
        self.trigger = trigger
        self.effect = effect

    def on_notify(self,event):
        if self.trigger(self.game,self,event):
            self.effect(self.game,self,event)
