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
        self.losing_balance = False
        self.off_balance = False
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
        self.off_balance=self.losing_balance
        self.losing_balance=False
        if self.alive:
            self.ai.update()

    def defense_roll(self): #agility - size
        if (self.ai and self.ai.state != AI_FIGHTING):
            return 0
        else:
            if self.off_balance:
                roll=(self.game.rng.stat_roll(self.agility//2)-self.size//3)
            else:
                roll = (self.game.rng.stat_roll(self.agility) - self.size/3)
            print "Defense",roll
            return roll

    def accuracy_roll(self): #agility + perception
        roll = (self.game.rng.stat_roll(self.agility) +
                self.game.rng.stat_roll(self.perception//2))
        print "Accuracy",roll
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

    def attack(self,thing,degree_mod=0,sound_multiplier=2):
        if thing.creature:
            event = Event(EVENT_ATTACK, actor=self.owner, target=thing)
            event.degree = (self.accuracy_roll()-thing.creature.defense_roll()) // DEGREE_OF_SUCCESS + 1 + degree_mod
            if event.degree>0:
                event.hit = True
                event.dealt, event.killed = thing.creature.take_damage(self.damage_roll(),event.degree)
                self.owner.make_sound(sound_multiplier)
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
