import libtcodpy as libtcod
from config import *
import logging

from event import Event
from entity import Entity

logger = logging.getLogger('entity')

class Player(Entity):
    def __init__(self,*args,**kwargs):
        if 'input_handler' in kwargs:
            self.input_handler = kwargs['input_handler']
            del kwargs['input_handler']
        else:
            self.input_handler = None
        if self.input_handler:
            self.input_handler.owner = self

        Entity.__init__(self,*args,**kwargs)

        self.materials = {}
        self.abilities = []
        self.words = []
        self.active = None
        self.ghost = False

    @property
    def fov(self):
        return self.creature.fov

    def harvest_corpse(self):
        """Harvests corpse at player tile, returns EVENT_HARVEST
        If there were no corpses, returns EVENT_NONE"""
        entity = self.game.get_item_at(*self.pos)
        if entity and entity.creature:
            self.add_materials(entity.creature.materials)
            self.game.entities.remove(entity)
            return self.notify(Event(EVENT_HARVEST,
                                     actor = self,
                                     corpse = entity,
                                     majority_material=entity.creature.majority_material))
        else:
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

    def add_trait(self,bp,trait):
        if type(bp) == str:
            bp = self.creature.body_parts[bp]
        if type(trait) == str:
            trait = self.game.traits[trait]

        if bp.can_add(trait) and self.can_afford(trait.cost):
            self.pay(trait.cost)
            return bp.add_trait(trait)
        else:
            return Event(EVENT_NONE)

    def remove_trait(self,bp,trait):
        if type(bp) == str:
            bp = self.creature.body_parts[bp]
        if type(trait) == str:
            trait = self.game.traits[trait]
    
        if bp.can_remove(trait) and self.can_afford(trait.removal_cost):
            self.pay(trait.removal_cost)
            return bp.remove_trait(trait)
        else:
            return Event(EVENT_NONE)
