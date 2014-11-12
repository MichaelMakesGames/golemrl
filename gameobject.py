import libtcodpy as libtcod
from config import *
import logging
import game
#import ai, physics, creature, item

class GameObject:
    def __init__(self,obj_id, ai_comp=None, physics_comp=None, creature_comp=None, item_comp=None):
        self.obj_id = obj_id

        self.ai_comp = ai_comp
        if ai_comp:
            self.ai_comp.owner = self

        self.physics_comp = physics_comp
        if physics_comp:
            self.physics_comp.owner = self

        self.creature_comp = creature_comp
        if creature_comp:
            self.creature_comp.owner = self

        self.item_comp = item_comp
        if item_comp:
            self.item_comp.owner = self

    def clear(self, focus_x, focus_y, con):
        render_x = self.physics_comp.x - focus_x + MAP_W//2
        render_y = self.physics_comp.y - focus_y + MAP_H//2
        con.put_char(render_x,render_y,' ')

    def render(self, focus_x, focus_y, con):
        if libtcod.map_is_in_fov(game.g.dungeon.tcod_map,self.physics_comp.x,self.physics_comp.y):
            char = color = None
            if self.creature_comp:
                char = self.creature_comp.char
                color = self.creature_comp.color
            elif self.item_comp:
                char = self.item_comp.char
                color = self.item_comp.char
            if char and color:
                render_x = self.physics_comp.x - focus_x + MAP_W//2
                render_y = self.physics_comp.y - focus_y + MAP_H//2
                con.set_default_foreground(color)
                con.put_char(render_x,render_y,char)

    def update(self):
        if self.ai_comp:
            self.ai_comp.update()

        if self.physics_comp:
            self.physics_comp.update()

        if self.creature_comp:
            self.creature_comp.update()

        if self.item_comp:
            self.item_comp.update()
