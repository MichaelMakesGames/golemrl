import libtcodpy as libtcod
from config import *
import logging

from observer import Observer, Subject
from event import Event

logger = logging.getLogger('thing')

class Thing(Subject):
    def __init__(self,thing_id,
                 x, y, depth, move_through, see_through,
                 creature=None, ai=None, item=None):
        Subject.__init__(self)

        self.thing_id = thing_id

        self.x = x
        self.y = y
        self.depth = depth
        self.move_through = move_through
        self.see_through = see_through
        self.ghost = False

        self.creature = creature
        if self.creature:
            self.creature.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.item = item
        if self.item:
            self.item.owner = self

    @property
    def level(self):
        return self.owner.dungeon.levels[self.depth]
    @property
    def pos(self):
        return (self.x,self.y)

    def clear(self, focus_x, focus_y, con):
        render_x = self.x - focus_x + MAP_W//2
        render_y = self.y - focus_y + MAP_H//2
        con.put_char(render_x,render_y,' ')

    def render(self, focus_x, focus_y, con):
        if libtcod.map_is_in_fov(self.owner.dungeon.tcod_map,self.x,self.y):
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

    def distance_to(self,x,y):
        return ((self.x-x)**2 + (self.y-y)**2)**0.5

    def move_to(self, new_x, new_y):
        logger.debug('Thing %i attempting move to (%i,%i)'%(self.thing_id,new_x,new_y))
        if (new_x >= self.level.first_col and
            new_x <= self.level.last_col and
            new_y >= self.level.first_row and
            new_y <= self.level.last_row):

            for thing in self.owner.things:
                if (thing.creature and thing.creature.alive and
                    thing.pos == (new_x,new_y)):
                    #self.creature.attack(thing)
                    return Event(EVENT_NONE)

            if (self.level(new_x,new_y).move_through) or self.ghost:
                logger.debug('Thing %i moved to (%i,%i)'%(self.thing_id,new_x,new_y))
                self.x = new_x
                self.y = new_y
                if self.creature:
                    self.notify('creature_moved')
                if self == self.owner.player:
                    self.notify('player_moved')
                return Event(EVENT_MOVE)

        return Event(EVENT_NONE)

    def move(self, dx, dy):
        return self.move_to(self.x+dx, self.y+dy)

    def move_or_attack(self, dx, dy):
        event = self.move(dx,dy)
        if event.event_type == EVENT_NONE:
            for thing in self.owner.things:
                if (thing.pos == (self.x+dx, self.y+dy) and
                    thing.creature and thing.creature.alive):
                    self.creature.attack(thing)
                    return Event(EVENT_ATTACK)
        return event #return either move or none, if attack not already returned

    def update(self):
        if self.creature:
            self.creature.update()
            if self.creature.alive and self.ai:
                self.ai.update()

        if self.item:
            self.item.update()
