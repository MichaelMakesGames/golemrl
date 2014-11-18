import libtcodpy as libtcod
from config import *
import logging
from tile import Tile
from level import Level
from room import Cave

logger = logging.getLogger('map')

class Dungeon:
    """Dungeon now is mostly a container for levels, and handles
    rendering"""
    def __init__(self, seed):
        logger.info('Making dungeon')
        self.rng = libtcod.random_new_from_seed(seed)
        self.messages = ['player_moved']
        
        self.levels = [None]
        passed = False
        attempt_num = 1
        while not passed and attempt_num < 10:
            logger.info('Generating level, attempt %i' % attempt_num)
            self.levels[0] = Level(self.rng,LEVEL_W,LEVEL_H)
            self.levels[0].owner = self
            self.levels[0].generate_caves()
            self.levels[0].smooth_caves()
            self.levels[0].find_caves()
            self.levels[0].remove_caves_by_size()
            self.levels[0].connect_caves()
            self.levels[0].remove_isolated_caves()
            if self.levels[0].evaluate():
                passed = True
                if EXPERIMENTAL_WALLS:
                    self.levels[0].mark_explorable()
                self.levels[0].tag_rooms()
            attempt_num += 1

        for level in self.levels:
            level.owner = self

        self.tcod_map = libtcod.map_new(LEVEL_W,LEVEL_H)
        #initialize tcod_map, cannot use compute_tcod_map because
        #dungeon is created before game
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
        for thing in self.owner.things:
            if thing != self.owner.player:
                x,y = thing.pos
                libtcod.map_set_properties(self.tcod_map,x,y,
                                           True,
                                           False)

    def blocking_thing_moved(self,from_x,from_y,to_x,to_y):
        libtcod.map_set_properties(self.tcod_map,from_x,from_y,True,True)
        libtcod.map_set_properties(self.tcod_map,to_x,to_y,True,False)

    def send(self, message):
        self.messages.append(message)

    def handle(self,message):
        if message == 'player_moved':
            player_x,player_y = self.owner.player.pos
            libtcod.map_compute_fov(self.tcod_map,
                                    player_x,
                                    player_y,
                                    15, True, 0)
            self.owner.cur_level.explore()
        elif message == 'creature_moved':
            self.compute_tcod_map()

        while message in self.messages:
            self.messages.remove(message)

    def update(self):
        while len(self.messages):
            self.handle(self.messages[0])

    def render(self, focus_x, focus_y, con):
        level = self.owner.cur_level
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

                        ### experimental wall rendering ###
                        if EXPERIMENTAL_WALLS and char == '#':
                            try:
                                #get the four neighbors of the tile
                                four = [level.get_tile(map_x,map_y-1), #N
                                        level.get_tile(map_x,map_y+1), #S
                                        level.get_tile(map_x+1,map_y), #E
                                        level.get_tile(map_x-1,map_y)] #W

                                for i in [0,1,2,3]:
                                    if four[i].explored:
                                        four[i] = four[i].char
                                    else:
                                        if ((four[i].char == '#' and
                                             not four[i].explorable and
                                             not four[i].explored) or
                                            (four[i].char == '.' and
                                             not four[i].explored)):
                                            #if tile is unexplorable wall
                                            #or unexplored floor, mark as
                                            #'?' instead of '.' or '#'
                                            #used to determine unseen half
                                            #of tile should be black
                                            four[i] = '?'
                                        else:
                                            four[i] = four[i].char
                                            
                                if four.count('#') == 2:
                                    #change char to diagonal
                                    if (four[0] == '#' and
                                        four[2] == '#'): #NE
                                        char = 227
                                    elif (four[0] == '#' and
                                          four[3] == '#'): #NW
                                        char = 226
                                    elif (four[1] == '#' and
                                          four[2] == '#'): #SE
                                        char = 229
                                    elif (four[1] == '#' and
                                          four[3] == '#'): #SW
                                        char = 232

                                    if char != '#':
                                        #the character was changed
                                        #colors need to be redone
                                        color = bkgnd
                                        if visible:
                                            bkgnd = C_FLOOR_BKGND
                                        else:
                                            bkgnd = C_FLOOR_BKGND_UNSEEN
                                        if four.count('?') > 1:
                                            #not sure how this works
                                            #if two or more tiles are
                                            #unexplorable walls or
                                            #unexplored floors, the
                                            #background should be black
                                            bkgnd = libtcod.black
                            except:
                                pass
                        ### end experiment wall rendering ###
                con.put_char_ex(x,y,char,color,bkgnd)

