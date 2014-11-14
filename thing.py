import libtcodpy as libtcod
from config import *
import logging
import game

class Thing:
    def __init__(self,obj_id,
                 x, y, level, move_through, see_through,
                 creature=None, ai=None, item=None):
        self.obj_id = obj_id

        self.x = x
        self.y = y
        self.level = level
        self.move_through = move_through
        self.see_through = see_through
        self.ghost = False

        self.creature = creature
        if creature:
            self.creature.owner = self

        self.ai = ai
        if ai:
            self.ai.owner = self

        self.item = item
        if item:
            self.item.owner = self

    def clear(self, focus_x, focus_y, con):
        render_x = self.x - focus_x + MAP_W//2
        render_y = self.y - focus_y + MAP_H//2
        con.put_char(render_x,render_y,' ')

    def render(self, focus_x, focus_y, con):
        if libtcod.map_is_in_fov(game.g.dungeon.tcod_map,self.x,self.y):
            char = color = None
            if self.creature:
                char = self.creature.char
                color = self.creature.color
            elif self.item:
                char = self.item.char
                color = self.item.char
            if char and color:
                render_x = self.x - focus_x + MAP_W//2
                render_y = self.y - focus_y + MAP_H//2
                con.set_default_foreground(color)
                con.put_char(render_x,render_y,char)

    @property
    def pos(self):
        return (self.x,self.y)

    def move_to(self, new_x, new_y):
        print new_x,new_y
        if (new_x >= self.level.first_col and
            new_x <= self.level.last_col and
            new_y >= self.level.first_row and
            new_y <= self.level.last_row):

            obj_positions = [obj.pos for obj in game.g.game_objects]
            for obj in game.g.game_objects:
                if (obj.creature and obj.creature.alive and
                    obj.pos == (new_x,new_y)):
                    self.creature.attack(obj)
                    return

            if (self.level(new_x,new_y).move_through) or self.ghost:
                self.x = new_x
                self.y = new_y
                if self.creature:
                    game.g.dungeon.send('creature_moved')

    def move(self, dx, dy):
        self.move_to(self.x+dx, self.y+dy)


    def update(self):
        if self.creature:
            self.creature.update()
            if self.creature.alive and self.ai:
                self.ai.update()

        if self.item:
            self.item.update()
