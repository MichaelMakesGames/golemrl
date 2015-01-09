import libtcodpy as libtcod
from config import *
import logging

from event import Event
from thing import Thing

logger = logging.getLogger('thing')

class Player(Thing):
    def __init__(self,*args,**kwargs):
        if 'input_handler' in kwargs:
            self.input_handler = kwargs['input_handler']
            del kwargs['input_handler']
        else:
            self.input_handler = None
        if self.input_handler:
            self.input_handler.owner = self

        Thing.__init__(self,*args,**kwargs)

        self.materials = {}
        self.spells = []
        self.words = []
        self.casting = None
        self.ghost = False

    @property
    def fov(self):
        return self.creature.fov

    def harvest_corpse(self):
        """Harvests corpse at player tile, returns EVENT_HARVEST
        If there were no corpses, returns EVENT_NONE"""
        thing = self.game.get_item_at(*self.pos)
        if thing and thing.creature:
            self.add_materials(thing.creature.materials)
            self.game.things.remove(thing)
            return self.notify(Event(EVENT_HARVEST,
                                     actor = self,
                                     corpse = thing,
                                     majority_material=thing.creature.majority_material))
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

    def can_cast(self,spell):
        return spell.can_cast(self)

    def cast(self,spell):
        if self.can_cast(spell) and self.can_afford(spell.cost):
            if spell.targeting == 'self':
                self.pay(spell.cost)
                return spell.cast(self)
            elif spell.targeting == 'touch' or spell.targeting == 'ranged':
                self.casting = spell
                return self.notify(Event(EVENT_START_SPELL,
                                         actor = self,
                                         spell = spell))

    def complete_spell(self,direction):
        spell = self.casting
        self.casting = None
        return (spell.cast(self,direction))

    def cancel_spell(self):
        spell = self.casting
        self.casting = None
        return self.notify(Event(EVENT_CANCEL_SPELL,
                                 actor=self,
                                 spell=spell))

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
