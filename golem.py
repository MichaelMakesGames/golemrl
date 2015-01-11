import libtcodpy as libtcod
from config import *
import logging

from event import Event
from creature import Creature
from fov import FOV

class Golem(Creature):
    def __init__(self,game,name,char,color,body_parts):
        self.game = game
        self.raw_name = name
        self.raw_char = char
        self.raw_color = color
        self.breed = self #WARNING so that code for handling other creatures works for players as well -- kinda messy...
        self.body_parts = body_parts
        self.fov = FOV(self.game,self)
        self.death_func=None
        self.ai=None

    @property
    def name(self): return self.raw_name
    @property
    def char(self):
        if self.alive:
            return self.raw_char
        else:
            return CORPSE_CHAR
    @property
    def color(self):
        if self.alive:
            return self.raw_color
        else:
            return C_CORPSE

    @property
    def max_health(self):
        return sum([self.body_parts[part].max_health
                    for part in self.body_parts])
    @property
    def size(self):
        return sum([self.body_parts[part].size
                    for part in self.body_parts])

    @property
    def intact_parts(self): return [self.body_parts[part_name]
                                    for part_name in self.body_parts
                                    if self.body_parts[part_name].intact]
    @property
    def agility(self):
        return sum([part.agility for part in self.intact_parts])
    @property
    def perception(self):
        return sum([part.perception for part in self.intact_parts])
    @property
    def strength(self):
        return sum([part.strength for part in self.intact_parts])

    @property
    def alive(self):
        return 0 not in [self.body_parts[part].health
                         for part in self.body_parts
                         if self.body_parts[part].vital]

    def update(self): pass

    def take_damage(self,damage_dealt,degree):
        part = self.game.rng.choose_weighted(self.intact_parts,
                                        lambda p: p.size)
        result = part.take_damage(damage_dealt,degree)
        if result[1]: self.die()
        return result

    def heal(self,part_name):
        clay = self.game.materials['CLAY']

        if (self.body_parts[part_name].damaged and
            clay in self.owner.materials and
            self.owner.materials[clay] >= 10):

            self.owner.materials[clay] -= 10
            self.body_parts[part_name].health += 1
            event = Event(EVENT_HEAL,
                          actor=self,
                          part=self.body_parts[part_name],
                          amount=1)
        else:
            event = Event(EVENT_NONE)
        
        return self.owner.notify(event)
