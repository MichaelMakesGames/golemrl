import logging
from creature import Creature

class Breed:
    def __init__(self,name,char,color,
                 health,agility,armor,perception,size,strength):
        self.name = name
        self.char = char
        self.color = color

        self.max_health = health
        self.agility = agility
        self.armor = armor
        self.perception = perception
        self.size = size
        self.strength = strength

    def new_creature(self):
        return Creature(self)
