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
        self.spells = []
        self.words = []
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

    def can_afford(self,cost):
        if cost == None:
            return False
        for material in cost:
            if self.materials[material] < cost[material]:
                return False
        return True

    def pay(self,cost):
        for material in cost:
            self.materials[material] -= cost[material]

    def toggle_ghost(self):
        self.ghost = not self.ghost
        event = Event(EVENT_TOGGLE_GHOST,enabled=self.ghost)
        self.notify(event)
        return event

    def knows_word(self,word):
        if word in self.words:
            return True
        else:
            return False
    def learn_word(self,word):
        if word not in self.words:
            self.append(word)

    def can_cast(self,spell):
        return spell.can_cast(self)

    def cast(self,spell,force=False):
        if self.can_cast(spell) and self.can_afford(spell.cost) or force:
            self.pay(spell.cost)
            spell.cast(self)

    def add_trait(self,bp,trait):
        if type(bp) == str:
            bp = self.creature.body_parts[bp]
        if type(trait) == str:
            trait = self.owner.traits[trait]

        if bp.can_add(trait) and self.can_afford(trait.cost):
            self.pay(trait.cost)
            return bp.add_trait(trait)
        else:
            return Event(EVENT_NONE)

    def remove_trait(self,bp,trait):
        if type(bp) == str:
            bp = self.creature.body_parts[bp]
        if type(trait) == str:
            trait = self.owner.traits[trait]
    
        if bp.can_remove(trait) and self.can_afford(trait.removal_cost):
            self.pay(trait.removal_cost)
            return bp.remove_trait(trait)
        else:
            return Event(EVENT_NONE)
