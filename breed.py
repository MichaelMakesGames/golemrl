import logging
from config import *

from event import Event
from thing import Thing
from creature import Creature
from ai import AI

class Breed:
    def __init__(self,game,breed_id,name,char,color,
                 health,agility,armor,perception,size,strength,materials,
                 death_func=None):
        self.game = game
        self.breed_id = breed_id
        self.name = name
        self.char = char
        self.color = color

        self.max_health = health
        self.agility = agility
        self.armor = armor
        self.perception = perception
        self.size = size
        self.strength = strength
        self.materials = materials
        self.death_func = death_func

    def new(self,x,y,depth):
        thing = Thing(self.game,self.game.next_id(),
                      x, y, depth, False, True,
                      creature = Creature(self.game,self))
        thing.add_observer(self.game.dungeon)
        thing.add_observer(self.game.message_log)
        for ability_id in self.game.abilities:
            thing.add_observer(self.game.abilities[ability_id])
        self.game.add_thing(thing)
        thing.notify(Event(EVENT_CREATE, actor=thing))
        thing.fov.refresh()
        return thing
