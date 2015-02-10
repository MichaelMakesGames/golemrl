import libtcodpy as libtcod
from config import *
import logging, yaml, os, time
import abilityfunctions, deathfunctions, yamlhelp
from entity import Entity
from player import Player
from inputhandler import InputHandler
from creature import Creature
from breed import Breed
from golem import Golem
from bodypart import BodyPart
from statuseffect import StatusEffect
from trait import Trait
from word import Word
from ability import Ability
from ai import AI
from tiletype import TileType
from prefab import Prefab
from dungeon import Dungeon
from console import Console
from messagelog import MessageLog
from rng import RNG
from material import Material

class Game:
    def __init__(self):
        self.rng = RNG()
        self.entities = []
        self.active_entities = []
        self.dungeon = None
        self.message_log = None
        self.menu = None
        self.overlay = None

        self.tile_types = {}
        self.materials = {}
        self.words = {}
        self.status_effects = {}
        self.traits = {}
        self.abilities = {}
        self.breeds = {}
        self.prefabs = {}
        self.active_region = []
        self.player = None
        self.fps=0

        self.map_con = Console("Dungeon Map",MAP_X,MAP_Y,MAP_W,MAP_H)
        self.panel_con = Console("Side Panel",PANEL_X,PANEL_Y,PANEL_W,PANEL_H)
        self.log_con = Console("Message Log",LOG_X,LOG_Y,LOG_W,LOG_H)

        self.state = STATE_PLAYING
        self.input_state = INPUT_NORMAL

    @property
    def depth(self):
        return self.player.depth
    @property
    def cur_level(self):
        return self.player.level

    @property
    def living_entities(self):
        return filter(lambda entity: entity.creature and entity.creature.alive, self.entities)

    def add_entity(self,entity):
        self.entities.append(entity)

    def next_id(self):
        next_id = 0
        id_list = [entity.entity_id for entity in self.entities]
        while True:
            if next_id not in id_list:
                return next_id
            else:
                next_id += 1

    def load_yaml(self):
        load_file = open('data/load.yaml')
        load_data = yaml.load(load_file)
        load_file.close()

        load_order = [('tiles',self.load_tile_types),
                      ('materials',self.load_materials),
                      ('words',self.load_words),
                      ('statuseffects',self.load_status_effects),
                      ('traits',self.load_traits),
                      ('abilities',self.load_abilities),
                      ('breeds',self.load_breeds),
                      ('prefabs',self.load_prefabs),
                      ('player',self.load_player)]

        for category in load_order:
            files = []
            if 'directories' in load_data[category[0]]:
                for directory in load_data[category[0]]['directories']:
                    for file_name in os.listdir(directory):
                        if file_name.endswith('.yaml'):
                            files.append(directory.strip('/')+'/'+file_name)
            if 'files' in load_data[category[0]]:
                for file_name in load_data[category[0]]['files']:
                    files.append(file_name)
            category[1](files)

    def load_tile_types(self,files):
        for file_name in files:
            f = open(file_name)
            data = yaml.load(f)
            f.close()
            yamlhelp.merge(data,self.tile_types)

        for tile_type_id in self.tile_types:
            tile_type = self.tile_types[tile_type_id]
            tile_type = TileType(tile_type_id,**tile_type)
            self.tile_types[tile_type_id] = tile_type

            if type(tile_type.color)==list:
                tile_type.color = [yamlhelp.load_color(c)
                                   for c in tile_type.color]
            else:
                tile_type.color = yamlhelp.load_color(tile_type.color)
            tile_type.color_not_visible = yamlhelp.load_color(tile_type.color_not_visible)

    def load_materials(self,files):
        for file_name in files:
            f = open(file_name)
            data = yaml.load(f)
            f.close()
            yamlhelp.merge(data,self.materials)

        for material_id in self.materials:
            material = self.materials[material_id]
            material = Material(material_id, **material)
            self.materials[material_id] = material

            material.color = yamlhelp.load_color(material.color)

    def load_status_effects(self,files):
        for file_name in files:
            f = open(file_name)
            data = yaml.load(f)
            f.close()
            yamlhelp.merge(data,self.status_effects)
        for status_effect_id in self.status_effects:
            status_effect = self.status_effects[status_effect_id]
            status_effect = StatusEffect(status_effect_id, **status_effect)
            self.status_effects[status_effect_id] = status_effect

    def load_traits(self,files):
        for file_name in files:
            f = open(file_name)
            data = yaml.load(f)
            f.close()
            yamlhelp.merge(data,self.traits)

        for trait_id in self.traits:
            trait = self.traits[trait_id]
            trait = Trait(trait_id,**self.traits[trait_id])
            self.traits[trait_id] = trait

        for trait_id in self.traits:
            #second pass needed since traits defs include other traits
            trait = self.traits[trait_id]
            if trait.replaces:
                trait.replaces = self.traits[trait.replaces]
            if not trait.cancels: trait.cancels=[]
            for i in range(len(trait.cancels)):
                trait.cancels[i] = self.traits[trait.cancels[i]]

            trait.effect = StatusEffect(trait_id,**trait.effect)

            if trait.cost:
                yamlhelp.convert_keys(trait.cost,self.materials)

            if trait.removal_cost:
                yamlhelp.convert_keys(trait.removal_cost,self.materials)

    def load_words(self,files):
        for file_name in files:
            f = open(file_name)
            data = yaml.load(f)
            f.close()
            yamlhelp.merge(data,self.words)

        for word_id in self.words:
            word = self.words[word_id]
            word = Word(word_id, **word)
            self.words[word_id] = word

            word.color = yamlhelp.load_color(word.color)

    def load_abilities(self,files):
        for file_name in files:
            f = open(file_name)
            data = yaml.load(f)
            f.close()
            yamlhelp.merge(data,self.abilities)

        for ability_id in self.abilities:
            ability = self.abilities[ability_id]
            ability = Ability(self, ability_id, **ability)
            self.abilities[ability_id] = ability
            ability.trigger = eval('abilityfunctions.%s'%ability.trigger)
            ability.effect  = eval('abilityfunctions.%s'%ability.effect)
            if ability.color:
                ability.color = yamlhelp.load_color(ability.color)

    def load_breeds(self,files):
        for file_name in files:
            f = open(file_name)
            data = yaml.load(f)
            f.close()
            yamlhelp.merge(data,self.breeds)

        for breed_id in self.breeds:
            breed = self.breeds[breed_id]
            breed = Breed(self, breed_id, **breed)
            self.breeds[breed_id] = breed

            breed.color = yamlhelp.load_color(breed.color)
            yamlhelp.convert_keys(breed.materials,self.materials)
            if breed.death_func:
                breed.death_func = eval('deathfunctions.%s' % \
                                        breed.death_func)

    def load_prefabs(self,files):
        for file_name in files:
            f = open(file_name)
            data = yaml.load(f)
            f.close()
            yamlhelp.merge(data,self.prefabs)

        for prefab_id in self.prefabs:
            prefab = self.prefabs[prefab_id]
            prefab = Prefab(prefab_id,**prefab)
            self.prefabs[prefab_id] = prefab

            for char in prefab.char_to_tile:
                if type(prefab.char_to_tile[char])==list:
                    prefab.char_to_tile[char] = [self.tile_types[t] for t in prefab.char_to_tile[char]]
                else:
                    prefab.char_to_tile[char] = self.tile_types[prefab.char_to_tile[char]]

    def load_player(self,files):
        player_data = {}
        for file_name in files:
            f = open(file_name)
            data = yaml.load(f)
            f.close()
            yamlhelp.merge(data,player_data)
        player_name = player_data.keys()[0]
        player_data = player_data[player_name]

        player_creature = Golem(self,player_name,**player_data)
        player_creature.raw_color = yamlhelp.load_color(player_creature.raw_color)
        for bp_name in player_creature.body_parts:
            bp = player_creature.body_parts[bp_name]
            bp = BodyPart(player_creature,bp_name,**bp)
            player_creature.body_parts[bp_name] = bp
            starting_trait_ids = bp.traits
            bp.traits = []
            for trait_id in starting_trait_ids:
                bp.add_trait(self.traits[trait_id],force=True)

        self.player = Player(self, self.next_id(),
                             0, 0, 0, False, True,
                             input_handler = InputHandler(),
                             creature = player_creature)
        self.add_entity(self.player)

        for name in self.materials:
            self.player.materials[self.materials[name]] = 0
        for ability in self.abilities.values():
            self.player.add_observer(ability)
            ability.add_observer(self.player.input_handler)
        self.player.creature.add_ability(self.abilities['HEAL'])
        self.player.creature.add_ability(self.abilities['CHARGE'])
        self.player.creature.add_ability(self.abilities['DODGE'])
        for word_id in self.words:
            self.player.words.append(self.words[word_id])

    def clear_all(self):
        for entity in self.entities:
            entity.clear(self.player.x,
                        self.player.y,
                        self.map_con)

    def get_entity(self,entity_id):
        for entity in self.entities:
            if entity.entity_id == entity_id:
                return entity

    def get_creature_at(self,x,y):
        return self.cur_level.get_tile(x,y).creature
    def get_item_at(self,x,y):
        return self.cur_level.get_tile(x,y).item

    def render_panel(self):
        self.panel_con.clear()
        self.panel_con.draw_border(True,C_BORDER,C_BORDER_BKGND)

        y = 2
        if SHOW_FPS:
            x=2
            self.panel_con.set_default_foreground(C_MENU)
            self.panel_con.print_string(x,y,'FPS: %i'%self.fps)
            y += 1

        y += 1
        for part_name in ['Head','Torso','L Arm','R Arm','L Leg','R Leg']:
            part = self.player.creature.body_parts[part_name]
            part_name = '%s:'%part.name
            part_health = '%i/%i'%(part.health,part.max_health)
            x = 2
            self.panel_con.set_default_foreground(C_MENU)
            self.panel_con.print_string(x,y,part_name)
            x = 9
            self.panel_con.set_default_foreground(libtcod.light_red)
            self.panel_con.print_string(x,y,part_health)
            y += 1

        status_effects = []
        for bp in self.player.creature.body_parts.values():
            status_effects += bp.status_effects
        if status_effects:
            y += 1
            for se in status_effects:
                if se.name:
                    x = 2
                    self.panel_con.set_default_foreground(C_MENU)
                    self.panel_con.print_string(x,y,se.name)
                    y += 1

        y += 1
        for material in sorted(self.player.materials):
            x = 2
            s = '%s: %i'%(material,self.player.materials[material])
            self.panel_con.set_default_foreground(material.color)
            self.panel_con.print_string(x,y,s)
            y += 1

        """y += 1
        for word in sorted(self.player.words):
            color = word.color
            x = 2
            self.panel_con.set_default_foreground(word.color)
            self.panel_con.print_string(x,y,word.name)
            y += 1"""

        y += 1
        self.panel_con.set_default_foreground(C_MENU)
        for stat in (('Size',self.player.creature.size),
                     ('Agility',self.player.creature.agility),
                     ('Perception',self.player.creature.perception),
                     ('Strength',self.player.creature.strength)):
            x = 2
            self.panel_con.print_string(x,y,'%s: %i'%stat)
            y += 1

    def render_all(self):
        player_x = self.player.x
        player_y = self.player.y
        if FOCUS == FOCUS_PLAYER:
            focus_x = player_x
            focus_y = player_y
        elif FOCUS == FOCUS_FIXED:
            focus_x = LEVEL_W//2
            focus_y = LEVEL_H//2

        self.dungeon.render(focus_x, focus_y, self.map_con,
                            overlay=self.overlay)
        for entity in self.entities:
            if entity != self.player:
                entity.render(focus_x, focus_y, self.map_con)
        for entity in self.living_entities: #draw living creatures on top
            if entity != self.player:
                entity.render(focus_x, focus_y, self.map_con)
        self.player.render(focus_x, focus_y, self.map_con)
        self.map_con.draw_border(True,C_BORDER,C_BORDER_BKGND)

        if self.menu:
            self.menu.render(self.map_con)
        self.map_con.blit()

        self.message_log.render(self.log_con)
        self.log_con.blit()

        self.render_panel()
        self.panel_con.blit()

    def play(self):
        key = libtcod.Key()
        mouse = libtcod.Mouse()

        t = time.time()
        while not libtcod.console_is_window_closed():
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
            self.clear_all()

            self.state = self.player.input_handler(key,mouse,
                                                   self.input_state,
                                                   self.menu)
            if self.menu and self.state != STATE_MENU:
                self.menu = None

            if self.state == STATE_PLAYING:
                player_room = self.cur_level.get_room_at(*self.player.pos)
                if player_room:
                    active_rooms = [player_room]
                    self.active_region = []
                    for room in player_room.connections:
                        if room not in active_rooms:
                            active_rooms.append(room)
                            for r in room.connections:
                                if r not in active_rooms:
                                    active_rooms.append(room)
                    for room in active_rooms:
                        self.active_region += room.tile_positions
                else:
                    self.active_region = [self.player.pos]
                self.active_entities=[]
                for entity in self.entities:
                    if entity.pos in self.active_region:
                        self.active_entities.append(entity)

                for entity in self.active_entities:
                    entity.update()
                self.state = STATE_PAUSED

            self.dungeon.update()
            self.render_all()
            libtcod.console_flush()
            self.fps = 1.0/(time.time()-t)
            t=time.time()

def new_game(seed = 0xDEADBEEF):
    game = Game()
    game.load_yaml()

    message_log = MessageLog(game)
    game.player.add_observer(message_log)
    for ability in game.abilities.values():
        ability.add_observer(message_log)
    game.player.input_handler.add_observer(message_log)
    game.message_log = message_log

    dungeon = Dungeon(game, seed)
    game.dungeon = dungeon
    game.player.add_observer(dungeon)
    start_pos = game.dungeon.generate_level(0)
    game.player.move_to(*start_pos)

    return game

def load_game(file_name):
    pass

def save_game(file_name):
    pass
