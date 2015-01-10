import libtcodpy as libtcod
from config import *
import logging

from event import Event

logger = logging.getLogger('ai')

class AI:
    def __init__(self,game,creature):
        self.game = game
        self.creature = creature
        self.state = AI_SLEEPING
        self.last_saw_player = 0
        self.path = None
        self.path_index = 0
        self.player_pos = (0,0)
    @property
    def thing(self):
        return self.creature.owner
    def update(self):
        tcod_map = self.game.dungeon.tcod_map        
        if not self.path:
            self.path = libtcod.path_new_using_map(tcod_map)

        pos = self.thing.pos
        visible = self.game.player.fov(*pos)
    
        done = False
        while not done:
            if self.state == AI_INACTIVE: #not used yet
                done = True
            elif self.state == AI_SLEEPING:
                if visible: #placeholder we put sound in
                    self.state = AI_RESTING
                    self.thing.notify(Event(EVENT_WAKE_UP,
                                            actor=self.thing))
                else: #continue sleeping
                    done = True
            elif self.state == AI_RESTING:
                self.creature.fov.refresh()
                if self.game.rng.get_float(0,1) < self.creature.fov(*self.creature.game.player.pos)/3.0: #1/3, 2/3, or 3/3 of noticing player depending where player is in fov
                    self.state = AI_FIGHTING
                    self.thing.notify(Event(EVENT_NOTICE,
                                            actor=self.thing))
                else: #TODO chance to start wandering or fall asleep
                    done = True

            elif self.state == AI_FIGHTING:
                if self.creature.fov(*self.game.player.pos):
                    self.last_saw_player = 0
                else: #increase last_saw_player and fall asleep if it's been too long
                    self.last_saw_player += 1
                    if self.last_saw_player >= 5:
                        self.state = AI_SLEEPING

                new_player_pos = self.game.player.pos #get latest player pos and recalculate path if needed
                if self.player_pos != new_player_pos:
                    self.player_pos = new_player_pos
                    self.compute_path(*self.player_pos)

                if (self.path_index < libtcod.path_size(self.path)
                    and self.game.player.creature.alive):#walk path
                    x,y = libtcod.path_get(self.path, self.path_index)
                    event = self.thing.move_to(x,y)
                    if event.event_type == EVENT_MOVE: #successfully moved, increase path index
                        self.path_index += 1
                        done = True
                    elif self.thing.distance_to(*self.player_pos) < 2:
                        #didn't move but can attack player
                        self.creature.attack(self.game.player)
                        done = True
                    else: #didn't move or attack, try new path
                        self.compute_path(*self.player_pos)
                else: #end of path and don't know where to go now
                    done = True
                self.creature.fov.refresh()

    def compute_path(self, x, y):
        self_x,self_y = self.thing.pos
        libtcod.path_compute(self.path, self_x, self_y, x, y)
        self.path_index = 0
