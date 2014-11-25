import libtcodpy as libtcod
from config import *
import logging

from thing import Thing

logger = logging.getLogger('thing')

class Player(Thing):
    def __init__(self,*args,**kwargs):
        Thing.__init__(self,*args,**kwargs)
        self.materials = {}

    def harvest_corpse(self):
        things_harvested = []
        for thing in self.owner.get_things_at(*self.pos):
            if thing.creature and not thing.creature.alive:
                self.add_materials(thing.creature.materials)
                things_harvested.append(thing)
        for thing in things_harvested: #remove corpses
            self.owner.things.remove(thing)

    def add_materials(self,materials):
        for material in materials:
            if material in self.materials:
                self.materials[material] += materials[material]
            else:
                self.materials[material] = materials[material]
