import libtcodpy as libtcod
from config import *
import logging

logger = logging.getLogger('ai')

class AI:
    def __init__(self):
        self.state = "sleeping"
        self.last_saw_player = 0
        self.path = None
        self.path_index = 0
        self.player_pos = (0,0)
    @property
    def game(self):
        return self.owner.game
    def update(self):
        tcod_map = self.game.dungeon.tcod_map        
        if not self.path:
            self.path = libtcod.path_new_using_map(tcod_map)

        pos = self.owner.pos
        visible = self.game.player.fov(*pos)
    
        action_taken = False
        while not action_taken:
            if self.state == "sleeping":
                if visible:
                    logger.info('Thing %i waking up'%self.owner.thing_id)
                    self.state = "awake"
                else:
                    action_taken = True

            elif self.state == "awake":
                if visible: #player sees thing, so thing sees player
                    self.last_saw_player = 0
                else: #increase last_saw_player and fall asleep if it's been too long
                    self.last_saw_player += 1
                    if self.last_saw_player >= 5:
                        logger.info('Thing %i falling asleep'%self.owner.thing_id)
                        self.state = "sleeping"

                new_player_pos = self.game.player.pos #get latest player pos and recalculate path if needed
                if self.player_pos != new_player_pos:
                    logger.debug('Thing %i saw player at (%i,%i)'%(self.owner.thing_id,new_player_pos[0],new_player_pos[1]))
                    self.player_pos = new_player_pos
                    self.compute_path(*self.player_pos)

                if (self.path_index < libtcod.path_size(self.path)
                    and self.game.player.creature.alive):#walk path
                    logger.debug('Thing %i walking path'%(self.owner.thing_id))
                    x,y = libtcod.path_get(self.path, self.path_index)
                    event = self.owner.move_to(x,y)
                    if event.event_type == EVENT_MOVE: #successfully moved, increase path index
                        self.path_index += 1
                        action_taken = True
                    elif self.owner.distance_to(*self.player_pos) < 2:
                        #didn't move but can attack player
                        self.owner.creature.attack(self.game.player)
                        action_taken = True
                    else: #didn't move or attack, try new path
                        logger.debug('Thing %i did not move or attack'%(self.owner.thing_id))
                        self.compute_path(*self.player_pos)
                else: #end of path and don't know where to go now
                    action_taken = True

    def compute_path(self, x, y):
        logger.debug('Thing %i setting path to (%i,%i)'%(self.owner.thing_id,x,y))
        self_x,self_y = self.owner.pos
        libtcod.path_compute(self.path, self_x, self_y, x, y)
        self.path_index = 0
