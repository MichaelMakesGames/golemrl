import libtcodpy as libtcod
from config import *
import logging
from observer import Observer, Subject
from rng import RNG
from tile import Tile
from level import Level
from room import Cave

logger = logging.getLogger('map')

class Dungeon(Observer):
    """Dungeon now is mostly a container for levels, and handles
    rendering"""
    def __init__(self, game, seed):
        logger.info('Making dungeon')
        self.game = game
        self.rng = RNG(seed=seed)
        self.levels = []
        for i in range(NUM_LEVELS):
            self.levels.append(self.rng.get_int(0,1000000))
        self.rng.delete()
        self.tcod_map = libtcod.map_new(LEVEL_W,LEVEL_H)

        #does the fov need to be refreshed (ie new level, player moved...)
        self.refresh_fov = True
        #does the tcod map need to be refreshed (ie terrain change)
        self.refresh_tcod = True
        #positions of things that block movement or sight
        self.creature_positions = []

    def generate_level(self,depth):
        seed = self.levels[depth]
        approved = False
        while not approved:
            self.levels[depth] = Level(self.game, seed, LEVEL_W, LEVEL_H)

            self.levels[depth].generate_caves()
            self.levels[depth].smooth_caves()
            self.levels[depth].find_caves()
            self.levels[depth].remove_caves_by_size()
            self.levels[depth].connect_caves()
            self.levels[depth].remove_isolated_caves()
            if self.levels[depth].evaluate():
                approved = True
            else:
                seed += 1

        if EXPERIMENTAL_WALLS:
            self.levels[depth].mark_explorable()
        self.levels[depth].tag_rooms()
        self.levels[depth].populate_rooms()
        self.compute_tcod_map()
        return self.levels[depth].get_start_pos()

    def compute_tcod_map(self):
        for x in range(LEVEL_W):
            for y in range(LEVEL_H):
                tile = self.game.cur_level.get_tile(x,y)
                libtcod.map_set_properties(self.tcod_map,x,y,
                                           tile.see_through,
                                           tile.move_through)
        for thing in self.game.things:
            if thing != self.game.player:
                x,y = thing.pos
                libtcod.map_set_properties(self.tcod_map,x,y,
                                           True,
                                           False)
    def refresh_creature_positions(self):
        for pos in self.creature_positions:
            tile = self.game.cur_level.get_tile(*pos)
            libtcod.map_set_properties(self.tcod_map,
                                       pos[0],pos[1],
                                       tile.see_through,
                                       tile.move_through)
        self.creature_positions = []
        for thing in self.game.living_things:
            self.creature_positions.append(thing.pos)
            if thing != self.game.player:
                libtcod.map_set_properties(self.tcod_map,
                                           thing.pos[0],thing.pos[1],
                                           thing.see_through,
                                           thing.move_through)

    def on_notify(self,event):
        if event.event_type == EVENT_MOVE:
            thing = event.actor
            from_tile = self.levels[thing.depth].get_tile(*event.from_pos)
            to_tile = self.levels[thing.depth].get_tile(*event.to_pos)
            if thing.creature and thing.creature.alive:
                from_tile.creature = None
                if to_tile.creature:
                    print 'WARNING: moving creature to where one already exists'
                to_tile.creature = thing
            elif thing.item:
                from_tile.item = None
                if to_tile.item:
                    print 'WARNING: moving item to where one already exists'
                to_tile.item = thing
            #TODO we don't need to do a full refresh
            self.refresh_creature_positions()
            if event.actor == self.game.player:
                self.refresh_fov = True
        elif event.event_type == EVENT_DIE:
            thing = event.actor
            tile = self.levels[thing.depth].get_tile(thing.x,thing.y)
            tile.creature = None
            if tile.item:
                print 'WARNING: setting corpse to item where item already exists'
            tile.item = thing
            #TODO we don't need a full refresh
            self.refresh_creature_positions()
        elif event == EVENT_HARVEST:
            thing = event.corpse
            tile = self.levels[thing.depth].get_tile(thing.x,thing.y)
            tile.item = None
        elif event == EVENT_CREATE:
            thing = event.actor
            tile = self.levels[thing.depth].get_tile(thing.x,thing.y)
            if thing.creature and thing.creature.alive:
                if tile.creature:
                    print 'WARNING: creating creature where one already exists'
                tile.creature = thing
            elif thing.item:
                if tile.item:
                    print 'WARNING: creating item where one already exists'
                tile.item = thing
            #TODO we don't need a full refresh
            self.refresh_creature_positions()

    def update(self):
        if self.refresh_tcod:
            self.compute_tcod_map()
            self.refresh_tcod = False

        if self.refresh_fov:
            libtcod.map_compute_fov(self.tcod_map,
                                    self.game.player.x,
                                    self.game.player.y)
            self.game.cur_level.explore()
            self.refresh_fov = False

    def render(self, focus_x, focus_y, con):
        level = self.game.cur_level
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
                            bkgnd = tile.background
                        else:
                            color = tile.color_not_visible
                            bkgnd = tile.background_not_visible

                        ### START OF EXPERIMENTAL WALL RENDERING ###
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
                                            bkgnd = self.game.tile_types[FLOOR_ID].background
                                        else:
                                            bkgnd = self.game.tile_types[FLOOR_ID].background_not_visible
                                        if four.count('?') > 1:
                                            #not sure how this works
                                            #if two or more tiles are
                                            #unexplorable walls or
                                            #unexplored floors, the
                                            #background should be black
                                            bkgnd = libtcod.black
                            except:
                                pass
                        ### END OF EXPERIMENTAL WALL RENDERING ###
                con.put_char_ex(x,y,char,color,bkgnd)

