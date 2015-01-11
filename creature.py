import libtcodpy as libtcod
from config import *
import logging

from event import Event
from fov import FOV
from ai import AI

logger = logging.getLogger('creature')

class Creature:
    def __init__(self, game, breed):
        self.game = game
        self.breed = breed
        self.health = breed.max_health
        self.fov = FOV(self.game,self)
        self.ai = AI(self.game,self)

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
    def max_health(self): return self.breed.max_health
    @property
    def agility(self): return self.breed.agility
    @property
    def armor(self): return self.breed.armor
    @property
    def perception(self): return self.breed.perception
    @property
    def size(self): return self.breed.size
    @property
    def strength(self): return self.breed.strength
    @property
    def materials(self): return self.breed.materials
    @property
    def majority_material(self):
        return sorted(self.materials,key=lambda m: self.materials[m])[-1]
    @property
    def death_func(self):
        return self.breed.death_func

    def update(self):
        if self.alive:
            self.ai.update()

    def defense_roll(self): #agility - size
        if (self.ai and self.ai.state != AI_FIGHTING):
            return 0
        else:
            roll = (self.game.rng.roll(self.agility,6) - self.size/20)
            return roll

    def accuracy_roll(self): #agility + perception
        roll = (self.game.rng.roll(self.agility,6) +
                self.game.rng.roll(self.perception/2,6))
        return roll

    def damage_roll(self): #strength + size?
        return self.strength

    def stumble_roll(self):
        return self.defense_roll()<5

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
            logger.warn('Something attacked dead creature (thing %i)'%(self.owner.thing_id))
            return 0,False

    def attack(self,thing):
        logger.info('Thing %i attacking thing %i'%(self.owner.thing_id,thing.thing_id))
        if thing.creature:
            event = Event(EVENT_ATTACK, actor=self.owner, target=thing)
            event.degree = (self.accuracy_roll()-thing.creature.defense_roll()) // DEGREE_OF_SUCCESS + 1
            if event.degree:
                event.hit = True
                event.dealt, event.killed = thing.creature.take_damage(self.damage_roll(),event.degree)
            else:
                event.hit = False
            return self.owner.notify(event)
        else:
            return Event(EVENT_NONE)

    def die(self):
        if self.death_func:
            self.death_func(self.game,self.owner)
        return self.owner.notify(Event(EVENT_DIE, actor=self.owner))

    @property
    def alive(self):
        return self.health > 0

    def hear(self,volume,x,y):
        if self.perception*10 > 100-volume:
            if self.ai:
                self.ai.sounds.append((volume,x,y))
            return self.owner.notify(Event(EVENT_HEAR,
                                           actor=self.owner,
                                           volume=volume,
                                           pos=(x,y)))
        else:
            return Event(EVENT_NONE)
