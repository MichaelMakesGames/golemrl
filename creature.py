import libtcodpy as libtcod
from config import *
import logging

from event import Event
from fov import FOV
from ai import AI
from statuseffect import StatusEffect, ActiveStatusEffect

logger = logging.getLogger('creature')

class Creature:
    def __init__(self, game, breed):
        self.game = game
        self.breed = breed
        self.health = breed.max_health
        self.fov = FOV(self.game,self)
        self.ai = AI(self.game,self)
        self.status_effects = []

    @property
    def name(self):
        if self.alive:
            return self.breed.name
        else:
            return "%s Corpse"%self.breed.name
    @property
    def char(self):
        if self.alive:
            return self.breed.char
        else:
            return CORPSE_CHAR
    @property
    def color(self):
        if self.alive:
            return self.breed.color
        else:
            return self.majority_material.color

    @property
    def max_health(self): return self.breed.max_health + self.health_mod
    @property
    def agility(self): return self.breed.agility + self.agility_mod
    @property
    def armor(self): return self.breed.armor + self.armor_mod
    @property
    def perception(self): return self.breed.perception + self.perception_mod
    @property
    def size(self): return self.breed.size + self.size_mod
    @property
    def strength(self): return self.breed.strength + self.strength_mod
    @property
    def health_mod(self):
        return sum([se.health_mod for se in self.status_effects])
    @property
    def agility_mod(self):
        return sum([se.agility_mod for se in self.status_effects])
    @property
    def armor_mod(self):
        return sum([se.armor_mod for se in self.status_effects])
    @property
    def perception_mod(self):
        return sum([se.perception_mod for se in self.status_effects])
    @property
    def size_mod(self):
        return sum([se.size_mod for se in self.status_effects])
    @property
    def strength_mod(self):
        return sum([se.strength_mod for se in self.status_effects])
    @property
    def accuracy_mod(self):
        return sum([se.accuracy_mod for se in self.status_effects])
    @property
    def defense_mod(self):
        return sum([se.sound for se in self.status_effects])
    @property
    def sound_mod(self):
        return sum([se.sound_mod for se in self.status_effects])

    @property
    def materials(self): return self.breed.materials

    @property
    def majority_material(self):
        return sorted(self.materials,key=lambda m: self.materials[m])[-1]
    @property
    def death_func(self):
        return self.breed.death_func

    def update(self):
        se_to_remove = []
        for se in self.status_effects:
            remove = se.update()
            if remove:
                se_to_remove.append(se)
        for se in se_to_remove:
            self.remove_status_effect(se)

        if self.alive:
            self.ai.update()

    def defense_roll(self): #agility - size
        if (self.ai and self.ai.state != AI_FIGHTING):
            return 0
        else:
            roll = (self.game.rng.stat_roll(self.agility) - self.size/3)
            roll += self.defense_mod
            return roll

    def accuracy_roll(self): #agility + perception
        roll = (self.game.rng.stat_roll(self.agility) +
                self.game.rng.stat_roll(self.perception//2))
        roll += self.accuracy_mod
        return roll

    def damage_roll(self): #strength + size?
        return self.strength//3

    def stumble_roll(self): #roll agility against size
        return self.game.rng.stat_roll(self.agility)>self.game.rng.stat_roll(self.size)

    def take_damage(self,damage_dealt,degree):
        '''Rolls for armor and calculates damage received
        Returns the damage received, and whether it died'''
        if self.alive: #don't take damage if dead
            damage_received = damage_dealt*degree - self.armor
            if damage_received < 0: damage_received = 0
            self.health -= damage_received
            if self.health <= 0:
                self.health = 0
                self.die()
                return (damage_received,True)
            else:
                return (damage_received,False)
        else:
            return 0,False
    def heal(self,amount):
        if self.alive:
            self.health += amount
            if self.health > self.max_health:
                self.health = self.max_health

    def attack(self,entity,sound_multiplier=2):
        if entity.creature:
            event = Event(EVENT_ATTACK, actor=self.owner, target=entity)
            event.degree = (self.accuracy_roll()-entity.creature.defense_roll()) // DEGREE_OF_SUCCESS + 1
            if event.degree>0:
                event.hit = True
                event.dealt, event.killed = entity.creature.take_damage(self.damage_roll(),event.degree)
                self.make_sound(sound_multiplier)
            else:
                event.hit = False
            return self.owner.notify(event)
        else:
            return Event(EVENT_NONE)

    def die(self):
        if self.ai:
            self.ai.state = AI_INACTIVE
        if self.death_func:
            self.death_func(self.game,self.owner)
        return self.owner.notify(Event(EVENT_DIE, actor=self.owner))

    @property
    def alive(self):
        return self.health > 0

    def hear(self,volume,x,y):
        if self.game.rng.percent(min(95,volume*(self.perception//3))):
            if self.ai:
                self.ai.sounds.append((volume,x,y))
            return self.owner.notify(Event(EVENT_HEAR,
                                           actor=self.owner,
                                           volume=volume,
                                           pos=(x,y)))
        else:
            return Event(EVENT_NONE)

    def add_status_effect(self,status_effect):
        #TODO status effect already active... stacks? replaces? nothing?
        if type(status_effect) == str:
            status_effect = self.game.status_effects[status_effect]
        self.status_effects.append(ActiveStatusEffect(status_effect,self))
        self.health += status_effect.health_mod
    def remove_status_effect(self,status_effect):
        to_remove = []
        if type(status_effect) == str:
            for se in self.status_effects:
                if se.status_effect.status_effect_id == status_effect:
                    to_remove.append(se)
        elif status_effect.__class__.__name__ == 'StatusEffect':
            for se in self.status_effects:
                if se.status_effect is status_effect:
                    to_remove.append(se)
        elif status_effect.__class__.__name__ == 'ActiveStatusEffect':
            if status_effect in self.status_effects:
                to_remove.append(status_effect)
        for se in to_remove:
            self.status_effects.remove(se)
            self.health -= se.health_mod

    def make_sound(self,multiplier=1,ignore_status_effects=False):
        if not ignore_status_effects:
            multiplier += self.sound_mod
        volume = multiplier*self.size*10
        for entity in self.game.active_entities:
            if (entity.creature and
                entity.creature.alive and
                not entity is self):
                entity.creature.hear(volume//max(1,self.owner.distance_to(*entity.pos)), *self.owner.pos)
