import libtcodpy as libtcod
from config import *
import logging

from dice import Dice

logger = logging.getLogger('creature')

class Creature:
    def __init__(self, breed):
        self.breed = breed
        self.health = breed.max_health

    @property
    def name(self): return self.breed.name
    @property
    def char(self): return self.breed.char
    @property
    def color(self): return self.breed.color
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

    def update(self):
        pass

    def defense_roll(self): #agility - size
        roll = (Dice(self.agility,6).roll() - self.size/20)
        print 'defense %i'%roll
        return roll

    def accuracy_roll(self): #agility + perception
        roll = (Dice(self.agility,6).roll() +
                Dice(self.perception/2,6).roll())
        print 'accuracy %i'%roll
        return roll

    def damage_roll(self): #strength + size?
        return self.strength

    def take_damage(self,damage_dealt):
        '''Rolls for armor and calculates damage received
        Returns the damage received, and whether it died
        Whatever attacked must call the objects .die() method if needed'''
        if self.alive: #don't take damage if dead
            damage_received = damage_dealt - self.armor
            if damage_received < 0: damage_received = 0
            self.health -= damage_received
            if self.health <= 0:
                self.health = 0
                return (damage_received,True)
            else:
                return (damage_received,False)
        else:
            logger.warn('Something attacked dead creature (thing %i)'%(self.owner.obj_id))
            return 0,False

    def attack(self,thing):
        logger.info('Thing %i attacking thing %i'%(self.owner.obj_id,thing.obj_id))
        game = self.owner.owner
        if thing.creature:
            if self.accuracy_roll() > thing.creature.defense_roll():
                dealt, killed = thing.creature.take_damage(self.strength)
                game.message('%s attacked %s for %i damage'%(self.name,thing.creature.name,dealt),C_COMBAT_MSG)
                if killed:
                    game.message('%s killed %s!'%(self.name,thing.creature.name),C_COMBAT_MSG)
                    thing.creature.die()
            else:
                game.message('%s missed %s'%(self.name,thing.creature.name),C_COMBAT_MSG)

    def die(self):
        self.char = CORPSE_CHAR
        self.color = C_CORPSE
        self.name += ' Corpse'
        self.owner.blocks_movement = False
        self.owner.notify('creature_died')

    @property
    def alive(self):
        return self.health > 0
