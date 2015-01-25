import libtcodpy as libtcod
from config import *
import logging
import networkx as nx
from tile import Tile
from room import Cave, Tunnel
from rng import RNG

from creature import Creature
from ai import AI
from entity import Entity
from event import Event

class Rect:
    def __init__(self,x,y,w,h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    @property
    def max_x(self):
        return self.x+self.w-1
    @property
    def max_y(self):
        return self.y+self.h-1
    @property
    def center_x(self):
        return (self.x+self.max_x)//2
    @property
    def center_y(self):
        return (self.y+self.max_y)//2
    @property
    def center(self):
        return (self.center_x,self.center_y)
    
    def __contains__(self,pos):
        x,y = pos
        return (x >= self.x and x <= self.max_x and
                y >= self.y and y <= self.max_y)

    def intersects(self,other):
        return ((self.x,self.y) in other or
                (self.x,self.max_y) in other or
                (self.max_x,self.y) in other or
                (self.max_x,self.max_y) in other)

class Level:
    """The Dungeon consists of several levels. This contains
    information on the tiles, focus, rooms, as well as functions used
    to generate maps."""
    def __init__(self,game,seed,w=LEVEL_W,h=LEVEL_H):
        self.game = game
        self.dungeon = game.dungeon
        if seed: #at one point a temp level is created with no rng
            self.rng = RNG(seed=seed)
        else:
            self.rng = RNG()

        self.x_offset = 0
        self.y_offset = 0

        self.tiles = [ [Tile(game.tile_types[WALL_ID]) for y in range(h) ] for x in range(w) ]
        self.rooms = []

    @property
    def w(self):
        return len(self.tiles)
    @property
    def h(self):
        return len(self.tiles[0])

    @property
    def first_row(self):
        return 0
    @property
    def last_row(self):
        return self.h -1
    @property
    def first_col(self):
        return 0
    @property
    def last_col(self):
        return self.w-1

    @property
    def num_floors(self):
        n = 0
        for col in self.tiles:
            for tile in col:
                if tile.move_through:
                    n += 1
        return n

    def get_tile(self,x,y,safe=True):
        if safe:
            try:
                return self.tiles[x][y]
            except:
                return Tile(self.game.tile_types[WALL_ID])
        else:
            return self.tiles[x][y]

    def get_neighbors(self,x,y):
        neighbors = []
        for neighbor_x in range(x-1,x+2):
            for neighbor_y in range(y-1,y+2):
                if not ( neighbor_x == x and neighbor_y == y):
                    try:
                        neighbors.append(self.get_tile(neighbor_x,neighbor_y))
                    except IndexError:
                        pass
        return neighbors

    def mark_explorable(self):
        for x in range(self.w):
            for y in range(self.h):
                explorable = False
                for neighbor in self.get_neighbors(x,y):
                    if neighbor.move_through:
                        explorable = True
                self.get_tile(x,y).explorable = explorable

    def __call__(self,x,y):
        return self.get_tile(x,y)

    def is_in_level(self,x,y):
        return x in range(self.w) and y in range(self.h)

    def is_in_bounds(self,x,y):
        return ( x > 1 and x < self.w-2 and
                 y > 1 and y < self.h-2 )

    @property
    def caves(self):
        return filter(lambda room: room.kind == 'Cave',
                      self.rooms)
    @property
    def tunnels(self):
        return filter(lambda room: room.kind == 'Tunnel',
                      self.rooms)

    def get_room_at(self,x,y):
        for room in self.rooms:
            if (x,y) in room:
                return room
        return None

    def is_room(self,x,y):
        return bool(self.get_room_at(x,y))

    def get_next_room_id(self):
        cur_id = 0
        room_ids = [room.room_id for room in self.rooms]
        while True:
            if cur_id in room_ids:
                cur_id += 1
            else:
                return cur_id

    def get_room(self,room_id):
        for room in self.rooms:
            if room.room_id == room_id:
                return room

    def remove_room(self,room):
        for pos in room.tile_positions:
            self.get_tile(*pos).change_type(self.game.tile_types[WALL_ID])
        self.rooms.remove(room)

    def get_start_pos(self):
        """Gets a random tile from the start room.
        Used for initializing the player"""
        for room in self.rooms:
            if room.has_tag(TAG_START):
                creature_positions = [entity.pos for entity
                                      in self.game.living_entities]
                start_pos = creature_positions[0]
                while start_pos in creature_positions:
                    start_pos = self.rng.choose(room.tile_positions)
                return start_pos

    def explore(self):
        """Called when player moves to mark seen tiles as explored"""
        for x in range(self.w):
            for y in range(self.h):
                if self.game.player.fov(x,y):
                    self.get_tile(x,y).explored = True

    def explore_all(self):
        for x in range(self.w):
            for y in range(self.h):
                self.get_tile(x,y).explored = True
        return Event(EVENT_EXPLORE_ALL)

    def explore_explorable(self):
        try: #check if tiles have been marked as explorable or not
            foo = self.get_tile(0,0).explorable
        except AttributeError: #if they haven't, mark them
            self.mark_explorable()

        for x in range(self.w):
            for y in range(self.h):
                tile = self.get_tile(x,y)
                tile.explored = tile.explorable
        return Event(EVENT_EXPLORE_EXPLORABLE)

    def create_rects(self,attempts,restrictions,
                     min_w,max_w,min_h,max_h,
                     overlaps_allowed=0):
        rects = []
        for i in range(attempts):
            w = self.rng.get_int(min_w,max_w+1)
            h = self.rng.get_int(min_h,max_h+1)
            x = self.rng.get_int(2,self.w-2-w)
            y = self.rng.get_int(2,self.h-2-h)
            new_rect = Rect(x,y,w,h)
            new_rect.overlaps = 0
            
            restricted = False
            for r in restrictions:
                if new_rect.intersects(r):
                    restricted = True
            if not restricted:
                overlaps = [r for r in rects if new_rect.intersects(r)]
                if (len(overlaps) <= overlaps_allowed and
                    overlaps_allowed not in [r.overlaps
                                             for r in overlaps]):
                    #not too many overlaps, and none of the overlapped rectangles already at maximum overlaps
                    for r in overlaps:
                        r.overlaps += 1
                        new_rect.overlaps += 1
                    rects.append(new_rect)

        return rects

    def automata_cave_gen(self,rect,
                          init_chance=0.375,
                          grow=4, starve=9, wither=3,
                          visits=0.5):
        """Automata cave generation based on Evil Science's method"""
        for x in range(rect.x, rect.x+rect.w):
            for y in range(rect.y, rect.y+rect.h):
                if (self.is_in_bounds(x,y) and
                    self.rng.get_float(0,1) < init_chance):
                    self.get_tile(x,y).change_type(self.game.tile_types[FLOOR_ID])

        num_visits = int(visits * rect.w * rect.h)
        for i in range(num_visits):
            x = self.rng.get_int(rect.x, rect.x+rect.w)
            y = self.rng.get_int(rect.y, rect.y+rect.h)
            
            if self.is_in_bounds(x,y):
                neighbors = self.get_neighbors(x,y)
                num_neighbor_floors = 0
                for neighbor in neighbors:
                    if neighbor.move_through:
                        num_neighbor_floors += 1

                if self.get_tile(x,y).move_through:
                    if num_neighbor_floors >= starve or num_neighbor_floors <= wither:
                        self.get_tile(x,y).change_type(self.game.tile_types[WALL_ID])
                else: #is wall
                    if num_neighbor_floors >= grow:
                        self.get_tile(x,y).change_type(self.game.tile_types[FLOOR_ID])

    def place_prefab(self,start_x,start_y,prefab):
        prefab_data = prefab.get_map_data(self.rng,
                                          self.rng.flip(),
                                          self.rng.flip())
        for x in range(prefab.w):
            for y in range(prefab.h):
                if prefab_data[y][x]:
                    self.get_tile(start_x+x,start_y+y).change_type(prefab_data[y][x])

    def rect_automata_cave_gen(self,restrictions=[],
                               attempts=80,
                               rect_min_w=4, rect_max_w=8,
                               rect_min_h=4, rect_max_h=8,
                               max_overlaps=1,
                               min_area=1200):
        rects = []
        total_area = 0
        while total_area < min_area:
            rects = self.create_rects(attempts, restrictions,
                                      rect_min_w,rect_max_w,
                                      rect_min_h,rect_max_h,
                                      max_overlaps)
            total_area = sum([r.w*r.h for r in rects])
        for r in rects:
            self.automata_cave_gen(r, 0.9, 7,9,5, 0.4)

    def smooth_caves(self, remove=5, fill=3):
        """final pass over all cellular automata to smoothen caves"""
        tmp_level = Level(self.game,None)
        tmp_level.tiles = [ [tile.clone() for tile in col] for col in self.tiles]
        tmp_level.x_offset = self.x_offset
        tmp_level.y_offset = self.y_offset
        for x in range(1, self.w-1):
            for y in range(1, self.h-1):
                if self.is_in_bounds(x,y):
                    neighbors = self.get_neighbors(x,y)
                    num_neighbor_floors = 0
                    for n in neighbors:
                        if n.move_through:
                            num_neighbor_floors += 1
                
                    if self.get_tile(x,y).move_through:
                        if num_neighbor_floors <= fill:
                            tmp_level.get_tile(x,y).change_type(self.game.tile_types[WALL_ID])

                    else:
                        if num_neighbor_floors >= remove:
                            tmp_level.get_tile(x,y).change_type(self.game.tile_types[FLOOR_ID])

        self.tiles = tmp_level.tiles

    def find_caves(self):
        """go through all tiles and used floodfill to find caves"""
        for x in range(1, self.w-1):
            for y in range(1, self.h-1):
                if self.get_tile(x,y).move_through and not self.is_room(x,y):
                    self.flood_fill_add_cave(x,y)

    def flood_fill_add_cave(self,x,y):
        """flood fill a cave and create a Cave object and add it to the
        list of rooms (room for optimization if needed)"""
        tile_positions = []

        q = []
        q.append((x,y))
        while len(q) > 0:
            n = q[-1]
            q = q[:-1]
            if self.get_tile(*n).move_through and n not in q:
                tile_positions.append(n)
                if (n[0]-1,n[1]) not in tile_positions and self.is_in_level(n[0]-1,n[1]):
                    q.append((n[0]-1,n[1]))
                if (n[0]+1,n[1]) not in tile_positions and self.is_in_level(n[0]+1,n[1]):
                    q.append((n[0]+1,n[1]))
                if (n[0],n[1]-1) not in tile_positions and self.is_in_level(n[0],n[1]-1):
                    q.append((n[0],n[1]-1))
                if (n[0],n[1]+1) not in tile_positions and self.is_in_level(n[0],n[1]+1):
                    q.append((n[0],n[1]+1))
        
        cave = Cave(self.get_next_room_id())
        cave.tile_positions = tile_positions
        self.rooms.append(cave)

    def remove_caves_by_size(self,min_size=12,max_size=150):
        """remove caves deemed too large or small"""
        caves_to_remove = []
        for cave in self.rooms:
            if len(cave) < min_size or len(cave) > max_size:
                caves_to_remove.append(cave)
        for cave in caves_to_remove:
            self.remove_room(cave)

    def connect_caves(self,tries_per_room=16,
                      max_turns=6,min_length=4,max_length=6):
        """connect caves by randomly growing tunnels out
        can probably be optimized"""
        for cave in self.caves:
            possible_starts = (cave.min_x_cells + cave.max_x_cells +
                               cave.min_y_cells + cave.max_y_cells)
            for try_num in range(tries_per_room):
                if possible_starts:
                    start_cell = self.rng.choose(possible_starts)
                    cur_x,cur_y = start_cell
                    start_room = self.get_room_at(*start_cell)
                    
                    abandon = False
                    connection = False
                    tunnel_positions = []
                    if start_cell in cave.min_y_cells:
                        cur_dir = 0 #north
                    elif start_cell in cave.max_y_cells:
                        cur_dir = 1 #south
                    elif start_cell in cave.max_x_cells:
                        cur_dir = 2 #east
                    elif start_cell in cave.min_x_cells:
                        cur_dir = 3 #west

                    for turn_num in range(max_turns+1):
                        if turn_num != 0: #turn if not first segment
                            dirs = []
                            if cur_dir < 2:
                                dirs = [cur_dir,2,2,2,3,3,3]
                            else:
                                dirs = [cur_dir,0,0,0,1,1,1]
                            cur_dir = self.rng.choose( dirs )
                        for i in range(self.rng.get_int(min_length,max_length)):
                            #now go forward a randomized number of spaces

                            #if i == 0 and turn_num != 0:
                            #    #just turned, check corner to avoid following:   .###
                            #    for neighbor in self.get_neighbors(cur_x,cur_y): #...
                            #        if neighbor.move_through:
                            #            print "Tunnel failed corner test"
                            #            abandon = True                           #.##

                            if cur_dir == 0: #north/up
                                cur_y -= 1
                            elif cur_dir == 1: #south/down
                                cur_y += 1
                            elif cur_dir == 2: #east/right
                                cur_x += 1
                            elif cur_dir == 3: #west/left
                                cur_x -= 1

                            if not connection and not abandon:
                                if not self.is_in_bounds(cur_x,cur_y):
                                    #abandon if tunnel goes out of bounds
                                    abandon = True
                                if (cur_x,cur_y) in tunnel_positions:
                                    abandon = True
                                    
                                if not abandon:
                                    connected_to = self.get_room_at(cur_x,cur_y)
                                else:
                                    connected_to = None

                                if connected_to:
                                    if ((connected_to == start_room) or
                                        (connected_to in self.tunnels) or
                                        (True in [connected_to in t.connections for t in start_room.connections])):
                                        #abandon if back connected to
                                        #starting room or connected to
                                        #other tunnel or already connected
                                        #to this room
                                        abandon = True
                                    else:
                                        connection = True
                                        
                                elif ((cur_dir >= 2 and (self.is_room(cur_x,cur_y+1) or
                                                         self.is_room(cur_x,cur_y-1))) or
                                      (cur_dir <= 1 and (self.is_room(cur_x+1,cur_y) or
                                                         self.is_room(cur_x-1,cur_y)))):
                                    #adjacent is room, abandon
                                    abandon = True
                                else:
                                    #hasn't found room or run off map
                                    #so append new pos to tunnel list
                                    tunnel_positions.append((cur_x,cur_y))

                    if connection and not abandon:
                        #dig tunnel if successful and make rooms
                        for pos in tunnel_positions:
                            self.get_tile(*pos).change_type(self.game.tile_types[FLOOR_ID])
                        tunnel = Tunnel(self.get_next_room_id())
                        tunnel.tile_positions = tunnel_positions
                        tunnel.add_connection(start_room)
                        tunnel.add_connection(connected_to)
                        self.rooms.append(tunnel)

                        #remove start cell from possible starts, so we don't
                        #try to make a tunnel where we already have one
                        possible_starts.remove(start_cell)

    def remove_isolated_caves(self):
        """finds largest cave network and removes other caves.
        Currently cannot remove tunnels connecting small networks"""

        #build networks
        cave_networks = []
        for cave in self.rooms:
            #find or create current caves network
            cur_network = None
            for network in cave_networks:
                if cave in network:
                    cur_network = network
            if cur_network == None:
                cave_networks.append([cave])
                cur_network = cave_networks[-1]

            #add connections to current cave's network
            #merge networks as necessary
            #empty network getting merged so loop isn't disrupted
            for connection in cave.connections:
                for network in cave_networks:
                    if connection in network:
                        if cur_network != network:
                            for room in network:
                                cur_network.append(room)
                            for i in range(len(network)):
                                network.remove(network[0])
                if connection not in cur_network:
                    cur_network.append(connection)

        #determine largest network
        largest_network = []
        for network in cave_networks:
            if len(network) > len(largest_network):
                largest_network = network

        #remove caves in networks other than largest
        for network in cave_networks:
            if network != largest_network:
                for room in network:
                    self.remove_room(room)

    def experimental_cave_gen(self):
        prefab_rects = self.create_rects(1, [], 15,15, 10,10, 0)
        #prefab_rects = self.create_rects(4, [], 6,6, 6,6, 0)
        self.rect_automata_cave_gen(restrictions=prefab_rects,
                                    min_area = 1000)
        self.smooth_caves()
        self.remove_caves_by_size()
        for r in prefab_rects:
            print 'Placing prefab at (%i,%i)'%(r.x,r.y)
            self.place_prefab(r.x,r.y,self.game.prefabs["CAVERN_POND_0"])
        self.find_caves()
        self.connect_caves()
        self.remove_isolated_caves()

    def evaluate(self,
                 min_connectivity = 1.0,
                 min_floors_to_walls = 0.2):
        """Evaluates if a map should be kept or discarded and regenerated
        Return True if it should be kept, False otherwise"""
        connectivity = float(len(self.tunnels)) / len(self.caves)
        num_floors = sum([len(room) for room in self.rooms])
        floors_to_walls = (float(num_floors) /
                           (self.w * self.h - num_floors))
        print "Connectivity: %s"%str(connectivity)
        print "Floors/walls: %s"%str(floors_to_walls)
        return (connectivity >= min_connectivity and
                floors_to_walls >= min_floors_to_walls)

    def tag_rooms(self):
        graph = nx.MultiGraph()
        for room in self.rooms:
            graph.add_node(room)
        for room in self.rooms:
            for connection in room.connections:
                w = len(room)**0.5 + len(connection)**0.5
                graph.add_edge(room,connection, weight=w)

        #find the two rooms that have the longest optimal path
        #these will be the start and the end
        longest_path = (None, None, 0)
        for from_cave in sorted(graph.nodes()):
            #could perhaps be optimized -- calculated some path twice
            paths = nx.single_source_dijkstra_path_length(graph,from_cave)
            for to_cave in sorted(paths):
                if paths[to_cave] > longest_path[2]:
                    longest_path = (from_cave, to_cave, paths[to_cave])
                    
        start = self.rng.get_int(0,1)
        end = abs(start-1)
        start = longest_path[start]
        end = longest_path[end]
        path = nx.dijkstra_path(graph,start,end)

        #set the start and end rooms, then rooms between as path
        start.tag(TAG_START)
        end.tag(TAG_END)
        for room in path:
            room.tag(TAG_PATH)

        #tag sizes
        for room in self.rooms:
            size = len(room)
            if size < 25:
                room.tag(TAG_SM)
            elif size < 75:
                room.tag(TAG_MD)
            else:
                room.tag(TAG_LG)

    def populate_rooms(self):
        for room in self.rooms:
            if room.has_tag(TAG_CAVE) and not room.has_tag(TAG_START):
                tile_positions = room.tile_positions[:]
                for i in range(self.rng.get_int(2,4)):
                    x, y = self.rng.choose(tile_positions)
                    depth = self.dungeon.levels.index(self)
                    tile_positions.remove( (x,y) )
                    breed_ids = sorted(self.game.breeds)
                    breed_id = self.rng.choose(breed_ids)
                    self.game.breeds[breed_id].new(x,y,depth)

    def __repr__(self):
        lines = [ '' for i in range(self.h) ]
        for y in range(self.h):
            for x in range(self.w):
                lines[y] += str(self.get_tile(x,y))
        return '\n'.join(lines)
