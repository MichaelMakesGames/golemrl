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
        self.energy = 0
        self.fov = FOV(self.game,self)
        self.death_func=None
        self.ai=None
        self.abilities=[]

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
    def accuracy_mod(self):
        return sum([part.accuracy_mod for part in self.intact_parts])
    @property
    def defense_mod(self):
        return sum([part.defense_mod for part in self.intact_parts])
    @property
    def sound_mod(self):
        return sum([part.sound_mod for part in self.intact_parts])
    @property
    def damage_mod(self):
        return sum([part.damage_mod for part in self.intact_parts])

    @property
    def speed(self):
        return sum([part.speed for part in self.intact_parts])

    @property
    def alive(self):
        return 0 not in [bp.health
                         for bp in self.body_parts.values()
                         if bp.vital]

    def update(self):
        for bp in self.body_parts.values():
            bp.update()

    def take_damage(self,damage_dealt,degree):
        part = self.game.rng.choose_weighted(self.intact_parts,
                                        lambda p: p.size)
        result = part.take_damage(damage_dealt,degree)
        if result[1]: self.die()
        return result

    def add_status_effect(self,status_effect):
        print "WARNING: Body part not specified for status effect; applying to torso"
        self.body_parts['Torso'].add_status_effect(status_effect)
    def remove_status_effect(self,status_effect):
        print "WARNING: Body part not specified for status effect; applying to torso"
        self.body_parts['Torso'].remove_status_effect(status_effect)

    def add_ability(self,ability):
        if type(ability)==str:
            ability = self.game.abilities[ability]
        if ability not in self.abilities:
            self.abilities.append(ability)

    def remove_ability(self,ability):
        if type(ability)==str:
            ability = self.game.abilities[ability]
        if ability in self.abilities:
            self.abilities.remove(ability)
