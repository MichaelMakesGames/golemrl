import libtcodpy as libtcod
from config import *
import logging

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
            print 'pass in ai loop'
            if self.state == AI_INACTIVE:
                done = True
            elif self.state == AI_SLEEPING:
                if visible:
                    self.creature.fov.refresh()
                    if self.game.rng.get_float(0,1) < self.creature.fov(*self.game.player.pos)/3.0:
                        logger.info('Thing %i waking up'%self.thing.thing_id)
                        self.state = AI_FIGHTING
                    else:
                        done = True
                else:
                    done = True

            elif self.state == AI_FIGHTING:
                if self.creature.fov(*self.game.player.pos):
                    self.last_saw_player = 0
                else: #increase last_saw_player and fall asleep if it's been too long
                    self.last_saw_player += 1
                    if self.last_saw_player >= 5:
                        logger.info('Thing %i falling asleep'%self.thing.thing_id)
                        self.state = AI_SLEEPING

                new_player_pos = self.game.player.pos #get latest player pos and recalculate path if needed
                if self.player_pos != new_player_pos:
                    logger.debug('Thing %i saw player at (%i,%i)'%(self.thing.thing_id,new_player_pos[0],new_player_pos[1]))
                    self.player_pos = new_player_pos
                    self.compute_path(*self.player_pos)

                if (self.path_index < libtcod.path_size(self.path)
                    and self.game.player.creature.alive):#walk path
                    logger.debug('Thing %i walking path'%(self.thing.thing_id))
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
                        logger.debug('Thing %i did not move or attack'%(self.thing.thing_id))
                        self.compute_path(*self.player_pos)
                else: #end of path and don't know where to go now
                    done = True
                self.creature.fov.refresh()

    def compute_path(self, x, y):
        logger.debug('Thing %i setting path to (%i,%i)'%(self.thing.thing_id,x,y))
        self_x,self_y = self.thing.pos
        libtcod.path_compute(self.path, self_x, self_y, x, y)
        self.path_index = 0
