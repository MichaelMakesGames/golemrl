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
    def __call__(self, key, mouse, menu=None):
        game = self.owner.owner
        key_char = chr(key.c)

        if menu:
            action_dict = menu.action_dict
        else:
            action_dict = {('r',False): ACTION_HARVEST,
                           ('h',False): ACTION_OPEN_HEAL_MENU,
                           ('t',False): 'self.manage_traits()',
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

        try:
            event = eval(action)
        except TypeError:
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
        self.owner.owner.menu = menu
        if menu == None:
            return Event(EVENT_MENU_CANCEL)
        else:
            return Event(EVENT_MENU_OPEN)

    def manage_traits(self):
        game = self.owner.owner
        golem = self.owner.creature
        d = {1: golem.body_parts['Head'],
             2: golem.body_parts['Torso'],
             3: golem.body_parts['L Arm'],
             4: golem.body_parts['R Arm'],
             5: golem.body_parts['L Leg'],
             6: golem.body_parts['R Leg']}
        print 'Select body part:'
        for option in d:
            print '(%i) %s'%(option, d[option].name)
        bp = d[int(raw_input())]
        print ''
        print '%s currently has the following traits:'%bp.full_name
        for trait in bp.traits:
            print trait.name
        possible_traits = []
        for trait_id in game.traits:
            if bp.can_add(game.traits[trait_id]):
                possible_traits.append(game.traits[trait_id])
        print ''
        print 'Can currently add the following traits:'
        for i in range(len(possible_traits)):
            print '(%i) %s' % (i+1, possible_traits[i].name)
        choice = int(raw_input('Enter number to select trait or \'0\' to cancel: ')) - 1
        if choice in range(len(possible_traits)):
            bp.add_trait(possible_traits[choice])
        
        
