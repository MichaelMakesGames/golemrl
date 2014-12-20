import libtcodpy as libtcod
from config import *
import logging

from event import Event
from thing import Thing

logger = logging.getLogger('thing')

class Player(Thing):
    def __init__(self,*args,**kwargs):
        Thing.__init__(self,*args,**kwargs)
        self.materials = {}
        self.ghost = False

    def harvest_corpse(self):
        """Harvests corpse at player tile, returns EVENT_HARVEST
        If there were no corpses, returns EVENT_NONE"""
        try:
            thing = filter(lambda thing: thing.creature and not thing.creature.alive, self.owner.get_things_at(*self.pos))[0]
            self.add_materials(thing.creature.materials)
            self.owner.things.remove(thing)
            event = Event(EVENT_HARVEST, majority_material=thing.creature.majority_material)
            self.notify(event)
            return event

        except IndexError:
            return Event(EVENT_NONE)

    def add_materials(self,materials):
        for material in materials:
            if material in self.materials:
                self.materials[material] += materials[material]
            else:
                self.materials[material] = materials[material]

    def can_afford(self,trait):
        if not trait.cost:
            return False
        for material in trait.cost:
            if self.materials[material] < trait.cost[material]:
                return False
        return True

    def can_afford_removal(self,trait):
        if not trait.removal_cost:
            return False
        for material in trait.removal_cost:
            if self.materials[material] < trait.removal_cost[material]:
                return False
        return True

    def toggle_ghost(self):
        self.ghost = not self.ghost
        event = Event(EVENT_TOGGLE_GHOST,enabled=self.ghost)
        self.notify(event)
        return event
