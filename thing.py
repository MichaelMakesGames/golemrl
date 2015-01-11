import libtcodpy as libtcod
from config import *
import logging

from observer import Observer, Subject
from event import Event

logger = logging.getLogger('thing')

class Thing(Subject):
    def __init__(self,game,thing_id,
                 x, y, depth, move_through, see_through,
                 creature=None, item=None):
        Subject.__init__(self)

        self.game = game
        self.thing_id = thing_id

        self.x = x
        self.y = y
        self.depth = depth
        self.move_through = move_through
        self.see_through = see_through

        self.creature = creature
        if self.creature:
            self.creature.owner = self

        self.item = item
        if self.item:
            self.item.owner = self

    @property
    def level(self):
        return self.game.dungeon.levels[self.depth]
    @property
    def pos(self):
        return (self.x,self.y)
    @property
    def fov(self):
        return self.creature.fov
    def clear(self, focus_x, focus_y, con):
        render_x = self.x - focus_x + MAP_W//2
        render_y = self.y - focus_y + MAP_H//2
        con.put_char(render_x,render_y,' ')

    def render(self, focus_x, focus_y, con):
        if self.game.player.fov(self.x,self.y):
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
        event = Event(EVENT_NONE)
        if (new_x >= self.level.first_col and
            new_x <= self.level.last_col and
            new_y >= self.level.first_row and
            new_y <= self.level.last_row):

            for thing in self.game.things:
                if (thing.creature and thing.creature.alive and
                    thing.pos == (new_x,new_y)):
                    #self.creature.attack(thing)
                    return Event(EVENT_NONE)

            if (self.level(new_x,new_y).move_through) or self.ghost:
                logger.debug('Thing %i moved to (%i,%i)'%(self.thing_id,new_x,new_y))
                event = Event(EVENT_MOVE,
                              actor=self,
                              from_pos=self.pos,
                              to_pos=(new_x,new_y))
                #make sound while moving
                if thing.creature and thing.creature.alive:
                    if thing.creature.stumble_roll():
                        self.make_sound(200)
                        self.notify(Event(EVENT_STUMBLE,actor=self))
                    else:
                        self.make_sound(100)
                self.x = new_x
                self.y = new_y

        return self.notify(event)

    def move(self, dx, dy):
        return self.move_to(self.x+dx, self.y+dy)

    def move_or_attack(self, dx, dy):
        event = self.move(dx,dy)
        if event.event_type == EVENT_NONE:
            for thing in self.game.things:
                if (thing.pos == (self.x+dx, self.y+dy) and
                    thing.creature and thing.creature.alive):
                    event = self.creature.attack(thing)
        return event #return either move or none, if attack not already returned

    def make_sound(self,volume):
        for thing in self.game.things:
            if (thing.creature and
                thing.creature.alive and
                not thing is self):
                thing.creature.hear(volume//self.distance_to(*thing.pos)**2, *self.pos)

    def update(self):
        if self.creature:
            self.creature.update()

        if self.item:
            self.item.update()
