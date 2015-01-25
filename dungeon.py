import libtcodpy as libtcod
from config import *
import logging, time
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
        #positions of entities that block movement or sight
        self.creature_positions = []

    def generate_level(self,depth):
        seed = self.levels[depth]
        approved = False
        while not approved:
            start = t = time.time()
            self.levels[depth] = Level(self.game, seed, LEVEL_W, LEVEL_H)
            print "Created level:    \t%s"%str(time.time()-t)
            '''t = time.time()
            self.levels[depth].rect_automata_cave_gen()
            print "Generated caves:  \t%s"%str(time.time()-t)
            t = time.time()
            self.levels[depth].smooth_caves()
            print "Smoothed caves:   \t%s"%str(time.time()-t)
            t = time.time()
            self.levels[depth].find_caves()
            print "Found caves:      \t%s"%str(time.time()-t)
            t = time.time()
            self.levels[depth].remove_caves_by_size()
            print "Removed caves (1):\t%s"%str(time.time()-t)
            t = time.time()
            self.levels[depth].connect_caves()
            print "Connected caves:  \t%s"%str(time.time()-t)
            t = time.time()
            self.levels[depth].remove_isolated_caves()
            print "Removed caves (2):\t%s"%str(time.time()-t)
            print "Total time:       \t%s"%str(time.time()-start)
            '''
            self.levels[depth].experimental_cave_gen()
            if self.levels[depth].evaluate() or True:
                approved = True
                print "Approved"
            else:
                seed += 1
                print "Rejected"
            print ""

        self.compute_tcod_map()
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
        for entity in self.game.entities:
            if entity != self.game.player:
                x,y = entity.pos
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
        for entity in self.game.living_entities:
            self.creature_positions.append(entity.pos)
            if entity != self.game.player:
                libtcod.map_set_properties(self.tcod_map,
                                           entity.pos[0],entity.pos[1],
                                           entity.see_through,
                                           entity.move_through)

    def on_notify(self,event):
        #WARNING: assumes items don't affect tcod map
        if event.event_type == EVENT_MOVE:
            entity = event.actor
            from_tile = self.levels[entity.depth].get_tile(*event.from_pos)
            to_tile = self.levels[entity.depth].get_tile(*event.to_pos)
            if entity.creature and entity.creature.alive:
                from_tile.creature = None
                to_tile.creature = entity
                if entity != self.game.player:
                    libtcod.map_set_properties(self.tcod_map,
                                               event.from_pos[0],
                                               event.from_pos[1],
                                               from_tile.see_through,
                                               from_tile.move_through)
                    libtcod.map_set_properties(self.tcod_map,
                                               event.to_pos[0],
                                               event.to_pos[1],
                                               entity.see_through,
                                               entity.move_through)
                                           
            elif entity.item:
                from_tile.item = None
                to_tile.item = entity
            if event.actor == self.game.player:
                self.refresh_fov = True

        elif event.event_type == EVENT_DIE:
            entity = event.actor
            tile = self.levels[entity.depth].get_tile(entity.x,entity.y)
            tile.creature = None
            libtcod.map_set_properties(self.tcod_map,
                                       entity.x, entity.y,
                                       tile.see_through,
                                       tile.move_through)
            if not tile.item:
                tile.item = entity
            else:
                placed_corpse = False
                x,y = entity.pos
                r = 1
                while not placed_corpse:
                    positions = []
                    for try_x in range(entity.x-r,entity.x+r+1):
                        positions.append((try_x,entity.y+r))
                        positions.append((try_x,entity.y-r))
                    for try_y in range(entity.y-r,entity.y+r+1):
                        positions.append((entity.x+r,try_y))
                        positions.append((entity.x-r,try_y))
                    i = 0
                    while i<len(positions) and not placed_corpse:
                        try_tile = self.levels[entity.depth].get_tile(*positions[i])
                        if try_tile.move_through and not try_tile.item:
                            try_tile.item = entity
                            placed_corpse = True
                            entity.x = positions[i][0]
                            entity.y = positions[i][1]
                        i += 1
                    r += 1

        elif event.event_type == EVENT_HARVEST:
            entity = event.corpse
            tile = self.levels[entity.depth].get_tile(entity.x,entity.y)
            tile.item = None

        elif event.event_type == EVENT_CREATE:
            entity = event.actor
            tile = self.levels[entity.depth].get_tile(entity.x,entity.y)
            if entity.creature and entity.creature.alive:
                tile.creature = entity
            elif entity.item:
                tile.item = entity
            libtcod.map_set_properties(self.tcod_map,
                                       entity.x, entity.y,
                                       entity.see_through,
                                       entity.move_through)

    def update(self):
        if self.refresh_tcod:
            self.compute_tcod_map()
            self.refresh_tcod = False

        if self.refresh_fov:
            #libtcod.map_compute_fov(self.tcod_map,
            #                        self.game.player.x,
            #                        self.game.player.y)
            self.game.player.fov.refresh()
            self.game.cur_level.explore()
            self.refresh_fov = False

    def render(self, focus_x, focus_y, con, overlay=None):
        level = self.game.cur_level
        x_offset = 0 + focus_x - MAP_W//2
        y_offset = 0 + focus_y - MAP_H//2
        
        for x in range(MAP_W):
            for y in range(MAP_H):
                map_x = x+x_offset
                map_y = y+y_offset

                char = ' '
                color = libtcod.black
                background = libtcod.black

                if map_x in range(level.w) and map_y in range(level.h):
                    tile = level.get_tile(map_x,map_y)
                    explored = tile.explored

                    if explored:
                        char = tile.char
                        visible = self.game.player.fov(map_x,map_y)
                        if visible:
                            color = tile.color
                            if overlay == OVERLAY_FOV:
                                fov_num = 0
                                for entity in self.game.active_entities:
                                    if self.game.player.fov(entity) and (not entity is self.game.player) and entity.creature.ai.state!=AI_SLEEPING and entity.creature.alive:
                                        fov_num = max(fov_num,entity.fov(map_x,map_y))
                                
                                if fov_num==1:
                                    background = libtcod.darkest_blue
                                elif fov_num==2:
                                    background = libtcod.darker_blue
                                elif fov_num==3:
                                    background = libtcod.dark_blue
                        else:
                            color = tile.color_not_visible

                con.put_char_ex(x,y,char,color,background)
