import libtcodpy as libtcod
from config import *
import logging

from observer import Subject
from event import Event
from menu import Menu

logger = logging.getLogger('input')

class InputHandler(Subject):
    def __init__(self):
        Subject.__init__(self)
    @property
    def game(self):
        return self.owner.game
    def __call__(self, key, mouse, menu=None, casting=None):
        key_char = chr(key.c)

        if casting:
            if casting.targeting=='touch' or casting.targeting=='ranged':
                action_dict = {libtcod.KEY_ESCAPE: ACTION_CANCEL_SPELL,
                               libtcod.KEY_UP: ACTION_CAST_N,
                               libtcod.KEY_DOWN: ACTION_CAST_S,
                               libtcod.KEY_RIGHT: ACTION_CAST_E,
                               libtcod.KEY_LEFT: ACTION_CAST_W,
                               libtcod.KEY_KP1: ACTION_CAST_SW,
                               libtcod.KEY_KP2: ACTION_CAST_S,
                               libtcod.KEY_KP3: ACTION_CAST_SE,
                               libtcod.KEY_KP4: ACTION_CAST_W,
                               libtcod.KEY_KP6: ACTION_CAST_E,
                               libtcod.KEY_KP7: ACTION_CAST_NW,
                               libtcod.KEY_KP8: ACTION_CAST_N,
                               libtcod.KEY_KP9: ACTION_CAST_NE}

        elif menu:
            action_dict = menu.action_dict
        else:
            action_dict = {('r',False): ACTION_HARVEST,
                           ('s',False): ACTION_OPEN_SPELL_MENU,
                           ('t',False): ACTION_OPEN_BODY_MENU,
                           ('g',True): ACTION_TOGGLE_GHOST,
                           ('e',True): ACTION_EXPLORE_EXPLORABLE,
                           ('a',True): ACTION_EXPLORE_ALL,
                           ('p',True): ACTION_PRINT_POS,
                           ('r',True): ACTION_PRINT_ROOM,
                           libtcod.KEY_UP: ACTION_MOVE_N,
                           libtcod.KEY_DOWN: ACTION_MOVE_S,
                           libtcod.KEY_RIGHT: ACTION_MOVE_E,
                           libtcod.KEY_LEFT: ACTION_MOVE_W,
                           libtcod.KEY_KP1: ACTION_MOVE_SW,
                           libtcod.KEY_KP2: ACTION_MOVE_S,
                           libtcod.KEY_KP3: ACTION_MOVE_SE,
                           libtcod.KEY_KP4: ACTION_MOVE_W,
                           libtcod.KEY_KP5: ACTION_WAIT,
                           libtcod.KEY_KP6: ACTION_MOVE_E,
                           libtcod.KEY_KP7: ACTION_MOVE_NW,
                           libtcod.KEY_KP8: ACTION_MOVE_N,
                           libtcod.KEY_KP9: ACTION_MOVE_NE}
        if menu:
            action = 'Event(EVENT_MENU_OPEN)'
        else:
            action = ACTION_NONE

        try:
            action = action_dict[(key_char,key.lctrl)]
        except KeyError:
            try:
                action = action_dict[key.vk]
            except KeyError: pass

        if type(action) == str:
            event = eval(action)
        else:
            event = action()

        if event == None:
            event = Event(EVENT_NONE)
            logger.warn('Action %s returned None'%repr(action))

        event_type = event.event_type
        if event_type == EVENT_NONE:
            return STATE_PAUSED
        elif event_type == EVENT_MENU_OPEN:
            return STATE_MENU
        elif event_type == EVENT_MENU_CANCEL:
            return STATE_PAUSED
        elif event_type == EVENT_MOVE:
            return STATE_PLAYING
        elif event_type == EVENT_ATTACK:
            return STATE_PLAYING
        elif event_type == EVENT_HARVEST:
            return STATE_PLAYING
        elif event_type == EVENT_WAIT:
            return STATE_PLAYING

    def set_menu(self,menu):
        self.game.menu = menu
        if menu == None:
            return Event(EVENT_MENU_CANCEL)
        else:
            return Event(EVENT_MENU_OPEN)

    def open_spell_menu(self):
        menu_options = []
        i = 1
        for spell in self.owner.spells:
            menu_options.append( {'input':(str(i),False),
                                  'name': spell.name,
                                  'action': 'self.owner.cast(self.owner.spells[%i])'%(i-1)} )
            if not self.owner.can_cast(spell):
                menu_options[-1]['name'] += ' (Cannot cast)'
            else:
                menu_options[-1]['name'] += ' (%s)'%str(spell.cost)[1:-1]
            i += 1
        menu = Menu('Select spell',menu_options)
        return self.set_menu(menu)

    def open_body_menu(self):
        menu_options = []
        bp_names = ['Head','Torso','L Arm','R Arm','L Leg','R Leg']
        for name in bp_names:
            menu_options.append( {'input':(str(bp_names.index(name)+1),False),
                                  'name': name,
                                  'action': 'self.open_bp_menu(%s)'%repr(name)})
        menu = Menu('Select body part',menu_options)
        return self.set_menu(menu)

    def open_bp_menu(self,bp_name):
        menu_options = [ {'input':('w',False),
                          'name': 'Inscribe word',
                          'action': 'self.open_inscribe_menu(%s)'%repr(bp_name)},
                         {'input':('e',False),
                          'name': 'Erase word',
                          'action':'self.open_erase_menu(%s)'%repr(bp_name)},
                         {'input':('t',False),
                          'name': 'Add trait',
                          'action':'self.open_add_trait_menu(%s)'%repr(bp_name)},
                         {'input':('r',False),
                          'name': 'Remove trait',
                          'action': 'self.open_remove_trait_menu(%s)'%repr(bp_name)} ]
        bp = self.owner.creature.body_parts[bp_name]
        words_text = '%s currently has %i blank inscription slots,\nand the following words inscribed: %s'%(bp.name, bp.words.count(None),str([w.name for w in bp.words if w])[1:-1])
        traits_text = '%s currently has the following traits: %s\n%s can currently add the following traits: %s'%(bp.name,str([t.name for t in bp.traits])[1:-1],bp.name,str([self.game.traits[t].name for t in self.game.traits if bp.can_add(self.game.traits[t])])[1:-1])
        menu_text = '\n\n'.join([bp.name,words_text,traits_text])
        menu = Menu(menu_text,menu_options)
        return self.set_menu(menu)        

    def open_inscribe_menu(self,bp_name):
        menu_options = []
        for word in self.owner.words:
            if not self.owner.creature.body_parts[bp_name].has_word(word):
                menu_options.append({'input':(word.char.lower(),False),
                                     'name': word.name,
                                     'action': 'self.owner.creature.body_parts[%s].inscribe(self.game.words[%s])'%(repr(bp_name),repr(word.word_id))})
        menu = Menu('Choose word to inscribe on %s'%bp_name,
                    menu_options)
        return self.set_menu(menu)

    def open_erase_menu(self,bp_name):
        menu_options = []
        for word in self.owner.creature.body_parts[bp_name].words:
            if word != None:
                menu_options.append({'input':(word.char.lower(),False),
                                     'name': word.name,
                                     'action': 'self.owner.creature.body_parts[%s].erase(self.game.words[%s])'%(repr(bp_name),repr(word.word_id))})
        menu = Menu('Choose word to erase from %s'%bp_name,menu_options)
        return self.set_menu(menu)

    def open_add_trait_menu(self,bp_name):
        menu_options = []
        bp = self.owner.creature.body_parts[bp_name]
        possible_traits = [self.game.traits[t] for t in self.game.traits if bp.can_add(self.game.traits[t])]
        for trait in possible_traits:
            menu_options.append({'input':(str(possible_traits.index(trait)+1),False),
                                 'name':'%s (%s)'%(trait.name,repr(trait.cost)[1:-1]),
                                 'action':'self.owner.add_trait(%s,%s)'%(repr(bp_name),repr(trait.trait_id))})
        menu = Menu('Choose trait to add to %s'%bp_name,menu_options)
        return self.set_menu(menu)

    def open_remove_trait_menu(self,bp_name):
        menu_options = []
        bp = self.owner.creature.body_parts[bp_name]
        possible_traits = [trait for trait in bp.traits if bp.can_remove(trait)]
        for trait in possible_traits:
            menu_options.append({'input':(str(possible_traits.index(trait)+1),False),
                                 'name':'%s (%s)'%(trait.name,repr(trait.removal_cost)[1:-1]),
                                 'action':'self.owner.remove_trait(%s,%s)'%(repr(bp_name),repr(trait.trait_id))})
        menu = Menu('Choose trait to remove from %s'%bp_name,menu_options)
        return self.set_menu(menu)
