import libtcodpy as libtcod
from config import *
import logging
import yaml
import spellfunctions
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
        self.player = None
        self.things = []
        self.dungeon = None
        self.message_log = None
        self.menu = None
        self.tile_types = {}
        self.breeds = {}
        self.materials = {}
        self.spells = {}
        self.words = {}

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
        thing.owner = self
        self.things.append(thing)

    def next_id(self):
        next_id = 0
        id_list = [thing.thing_id for thing in self.things]
        while True:
            if next_id not in id_list:
                return next_id
            else:
                next_id += 1

    def load_tile_types(self):
        tile_types_file = open('data/tiletypes.yaml')
        self.tile_types = yaml.load(tile_types_file)
        tile_types_file.close()
        for tile_type_id in self.tile_types:
            tile_type = self.tile_types[tile_type_id]
            tile_type = TileType(tile_type_id,**tile_type)
            self.tile_types[tile_type_id] = tile_type

            tile_type.color = eval('libtcod.%s'%tile_type.color.replace(' ','_'))
            tile_type.color_not_visible = eval('libtcod.%s'%tile_type.color_not_visible.replace(' ','_'))
            tile_type.background = eval('libtcod.%s'%tile_type.background.replace(' ','_'))
            tile_type.background_not_visible = eval('libtcod.%s'%tile_type.background_not_visible.replace(' ','_'))

    def load_materials(self):
        materials_file = open('data/materials.yaml')
        self.materials = yaml.load(materials_file)
        materials_file.close()
        for material_id in self.materials:
            material = self.materials[material_id]
            material = Material(material_id, **material)
            self.materials[material_id] = material

            material.color = eval('libtcod.' + material.color)
            material.text_color = eval('libtcod.' + material.text_color)

    def load_traits(self):
        traits_file = open('data/traits.yaml')
        self.traits = yaml.load(traits_file)
        traits_file.close()
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
                new_cost = {}
                for material in trait.cost:
                    new_cost[self.materials[material]] = trait.cost[material]
                trait.cost = new_cost

            if trait.removal_cost:
                new_removal_cost = {}
                for material in trait.removal_cost:
                    new_removal_cost[self.materials[material]] = trait.removal_cost[material]
                trait.removal_cost = new_removal_cost

    def load_words(self):
        words_file = open('data/words.yaml')
        self.words = yaml.load(words_file)
        words_file.close()
        for word_id in self.words:
            word = self.words[word_id]
            word = Word(word_id, **word)
            self.words[word_id] = word

            word.color = eval('libtcod.%s'%word.color.replace(' ','_'))
            word.text_color = eval('libtcod.%s'%word.text_color.replace(' ','_'))

    def load_spells(self):
        spells_file = open('data/spells.yaml')
        self.spells = yaml.load(spells_file)
        spells_file.close()
        for spell_id in self.spells:
            spell = self.spells[spell_id]
            spell = Spell(spell_id, **spell)
            self.spells[spell_id] = spell

            new_cost_dict = {}
            for material_id in spell.cost:
                new_cost_dict[self.materials[material_id]] = spell.cost[material_id]
            spell.cost = new_cost_dict

            if spell.requires == None:
                spell.requires = [None,None]
            else:
                spell.requires[1] = self.words[spell.requires[1]]
            spell.func = eval('spellfunctions.%s'%spell.func)
            spell.owner = self

    def load_breeds(self):
        breeds_file = open('data/breeds.yaml')
        self.breeds = yaml.load(breeds_file)
        breeds_file.close()
        for breed_id in self.breeds:
            breed = self.breeds[breed_id]
            breed = Breed(breed_id, **breed)
            self.breeds[breed_id] = breed

            color = 'libtcod.' + breed.color.replace(' ','_')
            breed.color = eval(color)

            new_materials_dict = {}
            for material_id in breed.materials:
                material = self.materials[material_id]
                new_materials_dict[material] = breed.materials[material_id]
            breed.materials = new_materials_dict

            breed.owner = self

    def clear_all(self):
        for thing in self.things:
            thing.clear(self.player.x,
                        self.player.y,
                        self.map_con)

    def get_thing(self,thing_id):
        for thing in self.things:
            if thing.thing_id == thing_id:
                return thing

    def get_things_at(self,x,y):
        things_at_pos = []
        for thing in self.things:
            if thing.pos == (x,y):
                things_at_pos.append(thing)
        return things_at_pos

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
            self.panel_con.set_default_foreground(material.text_color)
            self.panel_con.print_string(x,y,s)
            y += 1

        y += 1
        for word in sorted(self.player.words):
            color = word.text_color
            x = 2
            self.panel_con.set_default_foreground(word.text_color)
            self.panel_con.print_string(x,y,word.name)
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
    game.load_tile_types()
    game.load_materials()
    game.load_traits()
    game.load_words()
    game.load_spells()
    game.load_breeds()

    player_file = open('data/player.yaml')
    player_data = yaml.load(player_file)
    player_name = player_data.keys()[0]
    player_data = player_data[player_name]
    player_file.close()
    player_data['color'] = eval('libtcod.%s' % player_data['color'])
    for part_name in player_data['body_parts']:
        player_data['body_parts'][part_name] = BodyPart(part_name,**player_data['body_parts'][part_name])
    for part_name in player_data['starting_traits']:
        bp = player_data['body_parts'][part_name]
        for trait_id in player_data['starting_traits'][part_name]:
            bp.add_trait(game.traits[trait_id], force=True)
    del player_data['starting_traits']

    player_creature = Golem(player_name,**player_data)

    player = Player(0,
                    0, 0, 0, False, True,
                    creature = player_creature)

    player.input_handler = InputHandler()
    player.input_handler.owner = player
    for name in game.materials:
        player.materials[game.materials[name]] = 0
    for spell_id in game.spells:
        player.spells.append(game.spells[spell_id])
    for word_id in game.words:
        player.words.append(game.words[word_id])
    game.player = player
    game.add_thing(player)

    message_log = MessageLog()
    message_log.owner = game
    player.add_observer(message_log)
    player.input_handler.add_observer(message_log)
    game.message_log = message_log

    dungeon = Dungeon(game, seed)
    game.dungeon = dungeon
    player.add_observer(dungeon)
    start_pos = game.dungeon.generate_level(0)
    player.move_to(*start_pos)

    return game

def load_game(file_name):
    pass

def save_game(file_name):
    pass
