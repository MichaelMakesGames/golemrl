import libtcodpy as libtcod
from config import *
import logging
import networkx as nx
from tile import Tile
from room import Cave, Tunnel
from rng import RNG

from creature import Creature
from ai import AI
from thing import Thing
from event import Event

class Level:
    """The Dungeon consists of several levels. This contains
    information on the tiles, focus, rooms, as well as functions used
    to generate maps."""
    def __init__(self,seed,w=LEVEL_W,h=LEVEL_H):
        if seed: #at one point a temp level is created with no rng
            self.rng = RNG(seed=seed)
        else:
            self.rng = RNG()

        self.x_offset = 0
        self.y_offset = 0

        self.tiles = [ [Tile() for y in range(h) ] for x in range(w) ]
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
                if tile.is_floor():
                    n += 1
        return n

    def get_tile(self,x,y,safe=True):
        if safe:
            try:
                return self.tiles[x][y]
            except:
                return Tile()
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
                    if neighbor.is_floor():
                        explorable = True
                self.get_tile(x,y).explorable = explorable

    def __call__(self,x,y):
        return self.get_tile(x,y)

    def is_in_level(self,x,y):
        return x in range(self.w) and y in range(self.h)

    def is_in_bounds(self,x,y):
        return ( x > 0 and x < self.w-1 and
                 y > 0 and y < self.h-1 )

    @property
    def caves(self):
        return filter(lambda room: room.kind == 'Cave',
                      self.rooms)
    @property
    def tunnels(self):
        return filter(lambda room: room.kind == 'Tunnel',
                      self.rooms)

    def which_room(self,x,y):
        for room in self.rooms:
            if (x,y) in room:
                return room.room_id
        return -1

    def is_room(self,x,y):
        return self.which_room(x,y) != -1

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

    def remove_room(self,room_id):
        room = self.get_room(room_id)
        for pos in room.tile_positions:
            self.get_tile(*pos).make_wall()
            #self.get_tile(*pos).color_unseen = libtcod.red #DEBUG
        self.rooms.remove(room)

    def get_start_pos(self):
        """Gets a random tile from the start room.
        Used for initializing the player"""
        for room in self.rooms:
            if room.has_tag(TAG_START):
                creature_positions = [thing.pos for thing
                                      in self.owner.owner.living_things]
                start_pos = creature_positions[0]
                while start_pos in creature_positions:
                    start_pos = self.rng.choose(room.tile_positions)
                return start_pos

    def explore(self):
        """Called when player moves to mark seen tiles as explored"""
        for x in range(self.w):
            for y in range(self.h):
                if libtcod.map_is_in_fov(self.owner.tcod_map,x,y):
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

    def generate_caves(self, init_chance=0.7,
                       grow=7, starve=9, wither=5,
                       visits=1.0):
        """Automata cave generation based on Evil Science's method"""
        for x in range(self.w)[1:-1]:
            for y in range(self.h)[1:-1]:
                if (self.is_in_bounds(x,y) and
                    self.rng.get_float(0,1) < init_chance):
                    self.get_tile(x,y).make_floor()

        num_visits = int(visits * self.w * self.h)
        for i in range(num_visits):
            x = self.rng.get_int(1,self.w-1)
            y = self.rng.get_int(1,self.h-1)
            
            if self.is_in_bounds(x,y):
                neighbors = self.get_neighbors(x,y)
                num_neighbor_floors = 0
                for neighbor in neighbors:
                    if neighbor.is_floor():
                        num_neighbor_floors += 1
                        
                if self.get_tile(x,y).is_floor():
                    if num_neighbor_floors >= starve or num_neighbor_floors <= wither:
                        self.get_tile(x,y).make_wall()
                else: #is wall
                    if num_neighbor_floors >= grow:
                        self.get_tile(x,y).make_floor()

    def smooth_caves(self, remove=5, fill=3):
        """final pass over all cellular automata to smoothen caves"""
        tmp_level = Level(None)
        tmp_level.tiles = [ [tile.clone() for tile in col] for col in self.tiles]
        tmp_level.x_offset = self.x_offset
        tmp_level.y_offset = self.y_offset
        for x in range(1, self.w-1):
            for y in range(1, self.h-1):
                if self.is_in_bounds(x,y):
                    neighbors = self.get_neighbors(x,y)
                    num_neighbor_floors = 0
                    for n in neighbors:
                        if n.is_floor():
                            num_neighbor_floors += 1
                
                    if self.get_tile(x,y).is_floor():
                        if num_neighbor_floors <= fill:
                            tmp_level.get_tile(x,y).make_wall()

                    else:
                        if num_neighbor_floors >= remove:
                            tmp_level.get_tile(x,y).make_floor()

        self.tiles = tmp_level.tiles

    def find_caves(self):
        """go through all tiles and used floodfill to find caves"""
        for x in range(1, self.w-1):
            for y in range(1, self.h-1):
                if self.get_tile(x,y).is_floor() and not self.is_room(x,y):
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
            if self.get_tile(*n).is_floor() and n not in q:
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

    def remove_caves_by_size(self,min_size=12,max_size=200):
        """remove caves deemed too large or small"""
        caves_to_remove = []
        for cave in self.rooms:
            if len(cave) < min_size or len(cave) > max_size:
                caves_to_remove.append(cave.room_id)
        for cave in caves_to_remove:
            self.remove_room(cave)

    def connect_caves(self,tries_per_room=16,
                      max_turns=3,min_length=4,max_length=8):
        """connect caves by randomly growing tunnels out
        can probably be optimized"""
        for cave in self.caves:
            possible_starts = (cave.min_x_cells + cave.max_x_cells +
                               cave.min_y_cells + cave.max_y_cells)
            for try_num in range(tries_per_room):
                if possible_starts:
                    start_cell = self.rng.choose(possible_starts)
                    cur_x,cur_y = start_cell
                    start_room_id = self.which_room(*start_cell)
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
                            if cur_dir == 0 or cur_dir == 1: #go east/west
                                cur_dir = self.rng.get_int(2,3)
                            else: #go north/south
                                cur_dir = self.rng.get_int(0,1)
                        for i in range(self.rng.get_int(min_length,max_length)):
                            #now go forward a randomized number of spaces

                            if i == 0 and turn_num != 0:
                                #just turned, check corner to avoid following:   .###
                                for neighbor in self.get_neighbors(cur_x,cur_y): #...
                                    if neighbor.is_floor():                      #.##
                                        abandon = True                           #.##

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
                                elif self.is_room(cur_x,cur_y): #found room
                                    connected_to = self.which_room(cur_x,cur_y)
                                    if (connected_to == start_room_id or
                                        self.get_room(connected_to) in self.tunnels):
                                        #abandon if back starting room or connected to tunnel
                                        abandon = True
                                    else:
                                        connection = True
                                elif self.get_tile(cur_x,cur_y).is_floor():
                                    #not room but is floor
                                    #intersecting other tunnel, abandon
                                    abandon = True
                                elif ((cur_dir >= 2 and (self.get_tile(cur_x,cur_y+1,True).is_floor() or
                                                         self.get_tile(cur_x,cur_y-1,True).is_floor())) or
                                      (cur_dir <= 1 and (self.get_tile(cur_x+1,cur_y,True).is_floor() or
                                                         self.get_tile(cur_x-1,cur_y,True).is_floor()))):
                                    #adjacent is floor, abandon
                                    abandon = True
                                else:
                                    #hasn't found room or run off map
                                    #so append new pos to tunnel list
                                    tunnel_positions.append((cur_x,cur_y))

                    if connection:
                        #dig tunnel if successful and make rooms
                        for pos in tunnel_positions:
                            self.get_tile(*pos).make_floor()
                            #self.get_tile(*pos).color = libtcod.blue #DEBUG
                        tunnel = Tunnel(self.get_next_room_id())
                        tunnel.tile_positions = tunnel_positions
                        tunnel.add_connection(self.get_room(start_room_id))
                        tunnel.add_connection(self.get_room(connected_to))
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
                if cave.room_id in network:
                    cur_network = network
            if cur_network == None:
                cave_networks.append([cave.room_id])
                cur_network = cave_networks[-1]

            #add connections to current cave's network
            #merge networks as necessary
            #empty network getting merged so loop isn't disrupted
            for connection in cave.connections:
                for network in cave_networks:
                    if connection in network:
                        if cur_network != network:
                            for room_id in network:
                                cur_network.append(room_id)
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
                for room_id in network:
                    self.remove_room(room_id)

    def evaluate(self,
                 min_connectedness = 1.25,
                 min_floors_to_walls = 0.38):
        """Evaluates if a map should be kept or discarded and regenerated
        Return True if it should be kept, False otherwise"""
        connectedness = float(len(self.tunnels)) / len(self.caves)
        num_floors = sum([len(room) for room in self.rooms])
        floors_to_walls = (float(num_floors) /
                           (self.w * self.h - num_floors))

        return (connectedness >= min_connectedness and
                floors_to_walls >= min_floors_to_walls)

    def tag_rooms(self):
        graph = nx.MultiGraph()
        for cave in self.caves:
            graph.add_node(cave.room_id)
        for tunnel in self.tunnels:
            w = len(tunnel)
            graph.add_edge(*tunnel.connections, weight=w)

        #find the two rooms that have the longest optimal path
        #these will be the start and the end
        longest_path = (None, None, 0)
        for from_cave in graph.nodes():
            #could perhaps be optimized -- calculated some path twice
            paths = nx.single_source_dijkstra_path_length(graph,from_cave)
            for to_cave in paths:
                if paths[to_cave] > longest_path[2]:
                    longest_path = (from_cave, to_cave, paths[to_cave])
                    
        start = self.rng.get_int(0,1)
        end = abs(start-1)
        start = longest_path[start]
        end = longest_path[end]
        path = nx.dijkstra_path(graph,start,end)

        #set the start and end rooms, then rooms between as path
        self.get_room(start).tag(TAG_START)
        self.get_room(end).tag(TAG_END)
        for room_id in path:
            self.get_room(room_id).tag(TAG_PATH)

        #make Tunnels tunnels, and everything else off_path
        for room in self.rooms:
            size = len(room)
            if size < 25:
                room.tag(TAG_SM)
            elif size < 75:
                room.tag(TAG_MD)
            else:
                room.tag(TAG_LG)

    def populate_rooms(self):
        game = self.owner.owner
        for room in self.rooms:
            if room.has_tag(TAG_CAVE) and not room.has_tag(TAG_START):
                tile_positions = room.tile_positions[:]
                for i in range(self.rng.get_int(2,4)):
                    x, y = self.rng.choose(tile_positions)
                    depth = self.owner.levels.index(self)
                    tile_positions.remove( (x,y) )
                    breed_names = sorted(game.breeds)
                    breed_name = self.rng.choose(breed_names)
                    thing = game.breeds[breed_name].new(x,y,depth)
                    game.add_thing(thing)
        self.owner.on_notify(Event(EVENT_CREATE)) #bit of a hack, might cause bugs in the future -- you have been warned

    def __repr__(self):
        lines = [ '' for i in range(self.h) ]
        for y in range(self.h):
            for x in range(self.w):
                lines[y] += str(self.get_tile(x,y))
        return '\n'.join(lines)
