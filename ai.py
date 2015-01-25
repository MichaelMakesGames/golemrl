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
        self.sounds = []
        self.prev_dir = None
    @property
    def entity(self):
        return self.creature.owner
    def update(self):
        tcod_map = self.game.dungeon.tcod_map        
        if not self.path:
            self.path = libtcod.path_new_using_map(tcod_map)

        pos = self.entity.pos
        visible = self.game.player.fov(*pos)
    
        done = False
        while not done:
            if self.state == AI_INACTIVE: #not used yet
                done = True
            elif self.state == AI_SLEEPING:
                wake_up = False
                for s in self.sounds:
                    if self.game.rng.percent(min(95,s[0]*(self.creature.perception+5)/10)):
                        wake_up = True
                if self.creature.health < self.creature.max_health:
                    wake_up = True
                if wake_up:
                    self.state = AI_RESTING
                    self.entity.notify(Event(EVENT_WAKE_UP,
                                            actor=self.entity))
                else: #continue sleeping
                    done = True

            elif self.state == AI_RESTING:
                self.creature.fov.refresh()
                if self.check_for_player():
                    self.state = AI_FIGHTING
                    self.entity.notify(Event(EVENT_NOTICE,
                                            actor=self.entity))
                else: #continue to rest or wander?
                    if self.game.rng.percent(20):
                        done = True
                    else:
                        self.state = AI_WANDERING

            elif self.state == AI_WANDERING:
                self.creature.fov.refresh()
                if self.check_for_player():
                    self.state = AI_FIGHTING
                    self.entity.notify(Event(EVENT_NOTICE,
                                            actor=self.entity))
                else:
                    direction = (0,0)
                    while not (self.valid_movement(direction) or
                               self.game.cur_level.get_tile(self.entity.x+direction[0],self.entity.y+direction[1]).creature==self.game.player):

                        directions = [(1,1),(1,-1),(-1,1),(-1,-1),
                                      (0,1),(0,-1),(1,0),(-1,0)]
                        if self.prev_dir:
                            directions += [self.prev_dir]*6
                            if self.prev_dir[0]==0:
                                directions += [(1,self.prev_dir[1])]*2
                                directions += [(-1,self.prev_dir[1])]*2
                            elif self.prev_dir[1]==0:
                                directions += [(self.prev_dir[0],1)]*2
                                directions += [(self.prev_dir[0],-1)]*2
                            else:
                                directions += [(self.prev_dir[0],0)]*2
                                directions += [(0,self.prev_dir[1])]*2
                        direction = self.game.rng.choose(directions)
                    t = self.game.cur_level(self.entity.x+direction[0],
                                            self.entity.y+direction[1])
                    if self.game.rng.percent(10):
                        self.state = AI_RESTING
                        done=True
                    elif t.creature is self.game.player:
                        self.entity.notify(EVENT_NOTICE,
                                          actor=self.entity)
                        self.state = AI_FIGHTING
                    else:
                        self.entity.move_to(self.entity.x+direction[0],
                                           self.entity.y+direction[1])
                        self.prev_dir=direction
                        done=True

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
                    event = self.entity.move_to(x,y)
                    if event.event_type == EVENT_MOVE: #successfully moved, increase path index
                        self.path_index += 1
                        done = True
                    elif self.entity.distance_to(*self.player_pos) < 2:
                        #didn't move but can attack player
                        self.creature.attack(self.game.player)
                        done = True
                    else: #didn't move or attack, try new path
                        self.compute_path(*self.player_pos)
                else: #end of path and don't know where to go now
                    done = True

        self.sounds = []
        if self.state != AI_INACTIVE and self.state != AI_SLEEPING:
            self.creature.fov.refresh()

    def check_for_player(self):
        notice_player = False
        if self.creature.fov(self.game.player):
            for s in self.sounds:
                if (s[1],s[2])==self.game.player.pos:
                    notice_player = True
            if (self.game.rng.get_float(0,1) < self.creature.fov(self.game.player)/3.0): #1/3, 2/3, or 3/3 of noticing player depending where player is in fov
                notice_player = True
        return notice_player

    def valid_movement(self,direction):
        if direction==None:
            return False
        else:
            t = self.game.cur_level.get_tile(self.entity.x+direction[0],
                                             self.entity.y+direction[1])
            return t.move_through and t.creature==None

    def compute_path(self, x, y):
        self_x,self_y = self.entity.pos
        libtcod.path_compute(self.path, self_x, self_y, x, y)
        self.path_index = 0

