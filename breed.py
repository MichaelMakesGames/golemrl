import logging

from thing import Thing
from creature import Creature
from ai import AI

class Breed:
    def __init__(self,breed_id,name,char,color,
                 health,agility,armor,perception,size,strength,materials):
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

    def new(self,x,y,depth):
        thing = Thing(self.owner.next_id(),
                      x, y, depth, False, True,
                      creature = Creature(self),
                      ai = AI() )
        thing.add_observer(self.owner.dungeon)
        thing.add_observer(self.owner.message_log)
        return thing
