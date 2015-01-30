import libtcodpy as libtcod
from config import *

class StatusEffect:
    def __init__(self, status_effect_id, name='', turns=-1,
                 health_mod=0, agility_mod=0, armor_mod=0,
                 perception_mod=0, size_mod=0, strength_mod=0,
                 damage_mod=0, accuracy_mod=0, defense_mod=0,
                 word_slots_mod=0,
                 heal=0, damage=0, sound_mod=0):
                 
        self.status_effect_id = status_effect_id
        self.name = name
        self.turns = turns

        self.health_mod = health_mod
        self.agility_mod = agility_mod
        self.armor_mod = armor_mod
        self.perception_mod = perception_mod
        self.size_mod = size_mod
        self.strength_mod = strength_mod

        self.word_slots_mod = word_slots_mod

        self.damage_mod = damage_mod

        self.accuracy_mod = accuracy_mod
        self.defense_mod = defense_mod

        self.heal = heal
        self.damage = damage

        self.sound_mod = sound_mod #multiplier

class ActiveStatusEffect:
    def __init__(self,status_effect, creature, turns=None):
        self.turns_left=turns
        if self.turns_left == None:
            self.turns_left = status_effect.turns
        self.status_effect = status_effect
        self.creature = creature

    @property
    def health_mod(self): return self.status_effect.health_mod
    @property
    def agility_mod(self): return self.status_effect.agility_mod
    @property
    def armor_mod(self): return self.status_effect.armor_mod
    @property
    def perception_mod(self): return self.status_effect.perception_mod
    @property
    def size_mod(self): return self.status_effect.size_mod
    @property
    def strength_mod(self): return self.status_effect.strength_mod

    @property
    def damage_mod(self): return self.status_effect.damage_mod
    @property
    def accuracy_mod(self): return self.status_effect.accuracy_mod
    @property
    def defense_mod(self): return self.status_effect.defense_mod
    @property
    def damage(self): return self.status_effect.damage
    @property
    def heal(self): return self.status_effect.heal
    @property
    def sound_mod(self): return self.status_effect.sound_mod

    @property
    def word_slots_mod(self): return self.status_effect.word_slots_mod

    def update(self):
        #returns true if should be removed
        if self.turns_left == 0:
            return True
        else:
            self.turns_left -= 1
            self.creature.heal(self.heal)
            self.creature.take_damage(self.damage,1)
            return False
