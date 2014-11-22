import libtcodpy as libtcod
from config import *
import logging

from creature import Creature
from dice import Dice

class BodyPart:
    def __init__(self,name,health,size,armor,vital=False):
        self.name = name
        self.max_health = health
        self.health = health
        self.size = size
        self.armor = armor
        self.vital = vital

    @property
    def intact(self):
        return self.health > 0

    def take_damage(self,damage_dealt):
        if self.intact:
            damage_received = damage_dealt - self.armor
            if damage_received < 0: damage_received = 0
            self.health -= damage_received
            if self.health <= 0:
                self.health = 0
                return (damage_received, self.vital)
            else:
                return (damage_received, False)
        else:
            return (0,False)

class Golem(Creature):
    def __init__(self,name,char,color,
                 agility,perception,strength,body_parts):
        self.raw_name = name
        self.raw_char = char
        self.raw_color = color

        self.raw_agility = agility
        self.raw_perception = perception
        self.raw_strength = strength

        if type(body_parts) == dict:
            self.body_parts = body_parts
        elif type(body_parts) == list:
            self.body_parts = dict( [(part.name, part)
                                     for part in body_parts] )

    @property
    def name(self): return self.raw_name
    @property
    def char(self): return self.raw_char
    @property
    def color(self): return self.raw_color
    @property
    def agility(self): return self.raw_agility
    @property
    def perception(self): return self.raw_perception
    @property
    def strength(self): return self.raw_strength

    @property
    def size(self):
        return sum([self.body_parts[part].size
                    for part in self.body_parts])

    @property
    def alive(self):
        return 0 not in [self.body_parts[part].health
                         for part in self.body_parts
                         if self.body_parts[part].vital]

    @property
    def max_health(self):
        return sum([self.body_parts[part].max_health
                    for part in self.body_parts])

    @property
    def health(self):
        return sum([self.body_parts[part].health
                    for part in self.body_parts])

    def take_damage(self,damage_dealt):
        n = libtcod.random_get_int(0,0,self.size-1)
        size = 0
        for part in sorted(self.body_parts):
            size += self.body_parts[part].size
            if n < size:
                return self.body_parts[part].take_damage(damage_dealt)
