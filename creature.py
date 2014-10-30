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
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.die()

    def attack(self,obj):
        if obj.creature_comp:
            obj.creature_comp.take_damage(self.strength)

    def die(self):
        pass

    @property
    def alive(self):
        return self.health < 0
