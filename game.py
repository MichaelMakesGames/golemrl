import libtcodpy as libtcod
from config import *
import logging, yaml, os
import spellfunctions, yamlhelp
from thing import Thing
from player import Player
from inputhandler import InputHandler
from creature import Creature
from breed import Breed
from golem import Golem
from bodypart import BodyPart
from trait import Trait
from word import Word
from spell import Spell
from ai import AI
from tiletype import TileType
from dungeon import Dungeon
from console import Console
from messagelog import MessageLog
from rng import RNG
from material import Material

class Game:
    def __init__(self):
        self.rng = RNG()
        self.things = []
        self.dungeon = None
        self.message_log = None
        self.menu = None

        self.tile_types = {}
        self.materials = {}
        self.words = {}
        self.traits = {}
        self.spells = {}
        self.breeds = {}
        self.player = None

        self.map_con = Console("Dungeon Map",MAP_X,MAP_Y,MAP_W,MAP_H)
        self.panel_con = Console("Side Panel",PANEL_X,PANEL_Y,PANEL_W,PANEL_H)
        self.log_con = Console("Message Log",LOG_X,LOG_Y,LOG_W,LOG_H)

        self.state = STATE_PLAYING

    @property
    def depth(self):
        return self.player.depth
    @property
    def cur_level(self):
        return self.player.level

    @property
    def living_things(self):
        return filter(lambda thing: thing.creature and thing.creature.alive, self.things)

    def add_thing(self,thing):
        self.things.append(thing)

    def next_id(self):
        next_id = 0
        id_list = [thing.thing_id for thing in self.things]
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
                      ('traits',self.load_traits),
                      ('spells',self.load_spells),
                      ('breeds',self.load_breeds),
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

    def load_traits(self,files):
        for file_name in files:
            f = open(file_name)
            data = yaml.load(f)
            f.close()
            yamlhelp.merge(data,self.traits)

        for trait_id in self.traits:
            trait = self.traits[trait_id]
            if 'modifiers' in trait:
                for modifier in trait['modifiers']:
                    trait[modifier+'_mod'] = trait['modifiers'][modifier]
                del trait['modifiers']
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

    def load_spells(self,files):
        for file_name in files:
            f = open(file_name)
            data = yaml.load(f)
            f.close()
            yamlhelp.merge(data,self.spells)

        for spell_id in self.spells:
            spell = self.spells[spell_id]
            spell = Spell(self, spell_id, **spell)
            self.spells[spell_id] = spell

            yamlhelp.convert_keys(spell.cost,self.materials)

            if spell.requires == None:
                spell.requires = [None,None]
            else:
                spell.requires[1] = self.words[spell.requires[1]]
            spell.func = eval('spellfunctions.%s'%spell.func)

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

    def load_player(self,files):
        player_data = {}
        for file_name in files:
            f = open(file_name)
            data = yaml.load(f)
            f.close()
            yamlhelp.merge(data,player_data)
        player_name = player_data.keys()[0]
        player_data = player_data[player_name]

        player_creature = Golem(player_name,**player_data)
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
        self.add_thing(self.player)

        for name in self.materials:
            self.player.materials[self.materials[name]] = 0
        for spell_id in self.spells:
            self.player.spells.append(self.spells[spell_id])
        for word_id in self.words:
            self.player.words.append(self.words[word_id])

    def clear_all(self):
        for thing in self.things:
            thing.clear(self.player.x,
                        self.player.y,
                        self.map_con)

    def get_thing(self,thing_id):
        for thing in self.things:
            if thing.thing_id == thing_id:
                return thing

    def get_creature_at(self,x,y):
        return self.cur_level.get_tile(x,y).creature
    def get_item_at(self,x,y):
        return self.cur_level.get_tile(x,y).item

    def render_panel(self):
        self.panel_con.clear()
        self.panel_con.draw_border(True,C_BORDER,C_BORDER_BKGND)

        y = 2
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

        y += 1
        for material in sorted(self.player.materials):
            x = 2
            s = '%s: %i'%(material,self.player.materials[material])
            self.panel_con.set_default_foreground(material.color)
            self.panel_con.print_string(x,y,s)
            y += 1

        y += 1
        for word in sorted(self.player.words):
            color = word.color
            x = 2
            self.panel_con.set_default_foreground(word.color)
            self.panel_con.print_string(x,y,word.name)
            y += 1

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

        self.dungeon.render(focus_x, focus_y, self.map_con)
        for thing in self.things:
            if thing != self.player:
                thing.render(focus_x, focus_y, self.map_con)
        for thing in self.living_things: #draw living creatures on top
            if thing != self.player:
                thing.render(focus_x, focus_y, self.map_con)
        self.player.render(focus_x, focus_y, self.map_con)
        self.map_con.draw_border(True,C_BORDER,C_BORDER_BKGND)
        #self.map_con.blit()
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

        while not libtcod.console_is_window_closed():
            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE, key, mouse)
            self.clear_all()

            self.state = self.player.input_handler(key,mouse,
                                                   self.menu,
                                                   self.player.casting)
            if self.menu and self.state != STATE_MENU:
                self.menu = None

            if self.state == STATE_PLAYING:
                for thing in self.things:
                    thing.update()
                self.state = STATE_PAUSED

            self.dungeon.update()

            self.render_all()
            libtcod.console_flush()

def new_game(seed = 0xDEADBEEF):
    game = Game()
    game.load_yaml()

    message_log = MessageLog(game)
    game.player.add_observer(message_log)
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
