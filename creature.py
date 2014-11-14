import libtcodpy as libtcod
from config import *
import logging

class Creature:
    def __init__(self,name,char,color,
                 strength,max_health):
        self.name = name
        self.char = char
        self.color = color
        self.strength = strength
        self.max_health = max_health
        self.health = max_health

    def update(self):
        pass

    def take_damage(self,amount):
        if self.alive:
            self.health -= amount
            if self.health <= 0:
                self.health = 0
                self.die()

    def attack(self,thing):
        if thing.creature:
            self.owner.owner.message(self.name + ' hits ' +
                      thing.creature.name +
                      ' for ' + str(self.strength) + ' damage.',
                      C_COMBAT_MSG)
            thing.creature.take_damage(self.strength)

    def die(self):
        self.char = CORPSE_CHAR
        self.color = C_CORPSE
        self.owner.owner.message(self.name + ' dies!',C_COMBAT_MSG)
        self.name += ' Corpse'

    @property
    def alive(self):
        return self.health > 0
