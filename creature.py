import libtcodpy as libtcod
from config import *
import logging
import game

class Creature:
    def __init__(self,name,char,color,
                 strength,max_health):
        self.name = name
        self.char = char
        self.color = color
        self.strength = strength
        self.max_health = max_health
        self.health = max_health

    def render(self, focus_x, focus_y, con):
        level = self.owner.physics_comp.level
        dest_x = self.owner.physics_comp.x - focus_x + MAP_W//2
        dest_y = self.owner.physics_comp.y - focus_y + MAP_H//2
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, dest_x, dest_y,
                                 self.char, libtcod.BKGND_NONE)

    def update(self):
        pass

    def take_damage(self,amount):
        if self.alive:
            self.health -= amount
            if self.health <= 0:
                self.health = 0
                self.die()

    def attack(self,obj):
        if obj.creature_comp:
            game.g.message(self.name + ' hits ' +
                           obj.creature_comp.name +
                           ' for ' + str(self.strength) + ' damage.',
                           C_COMBAT_MSG)
            obj.creature_comp.take_damage(self.strength)

    def die(self):
        self.char = CORPSE_CHAR
        self.color = C_CORPSE
        game.g.message(self.name + ' dies!',C_COMBAT_MSG)
        self.name += ' Corpse'

    @property
    def alive(self):
        return self.health > 0
