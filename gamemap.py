import libtcodpy as libtcod
from config import *
import logging
from tile import Tile
from level import Level
from room import Cave
import game

logger = logging.getLogger('map')

class GameMap:
    """GameMap now is mostly a container for levels, and handles
    rendering"""
    def __init__(self, seed):
        logger.info('Making game map')
        self.rng = libtcod.random_new_from_seed(seed)
        self.messages = ['player_moved']
        
        self.levels = [None]
        passed = False
        attempt_num = 1
        while not passed and attempt_num < 10:
            logger.info('Generating level, attempt %i' % attempt_num)
            self.levels[0] = Level(self.rng,LEVEL_W,LEVEL_H)
            self.levels[0].generate_caves()
            self.levels[0].smooth_caves()
            self.levels[0].find_caves()
            self.levels[0].remove_caves_by_size()
            self.levels[0].connect_caves()
            self.levels[0].remove_isolated_caves()
            if len(self.levels[0].rooms) >= 15:
                passed = True
            attempt_num += 1

        for level in self.levels:
            level.owner = self

        self.tcod_map = libtcod.map_new(LEVEL_W,LEVEL_H)
        #initialize tcod_map, cannot use compute_tcod_map because game
        #has game_map is created before game
        for x in range(LEVEL_W):
            for y in range(LEVEL_H):
                tile = self.levels[0].get_tile(x,y)
                libtcod.map_set_properties(self.tcod_map,x,y,
                                           tile.see_through,
                                           tile.move_through)

    def compute_tcod_map(self):
        for x in range(LEVEL_W):
            for y in range(LEVEL_H):
                tile = self.levels[0].get_tile(x,y)
                libtcod.map_set_properties(self.tcod_map,x,y,
                                           tile.see_through,
                                           tile.move_through)
        for obj in game.g.game_objects:
            x,y = obj.physics_comp.pos
            libtcod.map_set_properties(self.tcod_map,x,y,
                                       True,
                                       False)

    def send(self, message):
        self.messages.append(message)

    def handle(self,message):
        if message == 'player_moved':
            player_x,player_y = game.g.player.physics_comp.pos
            libtcod.map_compute_fov(self.tcod_map,
                                    player_x,
                                    player_y,
                                    15, True, 0)
            self.levels[game.g.cur_level].explore()
        elif message == 'creature_moved':
            self.compute_tcod_map()

        while message in self.messages:
            self.messages.remove(message)

    def update(self):
        while len(self.messages):
            self.handle(self.messages[0])

    def render(self, level_index, focus_x, focus_y, con):
        level = self.levels[level_index]
        x_offset = 0 + focus_x - MAP_W//2
        y_offset = 0 + focus_y - MAP_H//2
        
        for x in range(MAP_W):
            for y in range(MAP_H):
                map_x = x+x_offset
                map_y = y+y_offset

                char = ' '
                color = libtcod.black
                bkgnd = libtcod.black

                if map_x in range(level.w) and map_y in range(level.h):
                    tile = level.get_tile(map_x,map_y)
                    explored = tile.explored

                    if explored:
                        char = tile.char
                        visible = libtcod.map_is_in_fov(self.tcod_map,map_x,map_y)
                        if visible:
                            color = tile.color
                            bkgnd = tile.bkgnd
                        else:
                            color = tile.color_unseen
                            bkgnd = tile.bkgnd_unseen

                con.put_char_ex(x,y,char,color,bkgnd)

