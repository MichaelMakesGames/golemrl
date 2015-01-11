from config import *
import libtcodpy as libtcod
import logging

import textwrap
import util
from observer import Observer

logger = logging.getLogger('message')

class MessageLog(Observer):
    def __init__(self,game):
        self.game = game
        self.lines = []

    def on_notify(self,event):
        message = color = None

        ### Combat events ###
        if event.event_type == EVENT_ATTACK:
            color = C_COMBAT_MSG
            if event.hit:
                if event.degree == 1:
                    adjective = 'glancing'
                elif event.degree == 2:
                    adjective = 'solid'
                elif event.degree == 3:
                    adjective = 'well-placed'
                else:
                    adjective = 'critical'

                if event.killed:
                    message = '%s landed a %s hit, killing %s' % \
                              (event.actor.creature.name,
                               adjective,
                               event.target.creature.breed.name)
                else:
                    message = '%s landed a %s hit on %s, dealing %i damage' % \
                              (event.actor.creature.name,
                               adjective,
                               event.target.creature.name,
                               event.dealt)
            else:
                message = '%s missed %s' % \
                          (event.actor.creature.name,
                           event.target.creature.name)

        ### Trait events ###
        elif event.event_type == EVENT_ADD_TRAIT:
            message = 'Trait \'%s\' added to %s' % \
                      (event.trait.name, event.body_part.name)
            color = C_EFFECT_MSG
        elif event.event_type == EVENT_REMOVE_TRAIT:
            message = 'Trait \'%s\' removed from %s' % \
                      (event.trait.name, event.body_part.name)
            color = C_EFFECT_MSG
            
        ### Word events ###
        elif event.event_type == EVENT_INSCRIBE:
            message = 'You feel the powers of %s %s through your %s' % \
                      (event.word.name,
                       event.word.verb,
                       event.body_part.name)
            color = event.word.color
        elif event.event_type == EVENT_ERASE:
            message = 'You feel the powers of %s leave your %s' % \
                      (event.word.name, event.body_part.name)
            color = event.word.color

        ### Spell events ###
        elif event.event_type == EVENT_START_SPELL:
            message = 'You start casting %s - choose a direction' % \
                      (event.spell.name)
            try:
                color = event.spell.word.color
            except AttributeError:
                color = C_MENU
        elif event.event_type == EVENT_CANCEL_SPELL:
            message = 'You change your mind'
            try:
                color = event.spell.word.color
            except AttributeError:
                color = C_MENU
        elif event.event_type == EVENT_CAST_SPELL:
            message = 'You cast %s'%(event.spell.name)
            try:
                color = event.spell.word.color
            except AttributeError:
                color = C_MENU

        ### Misc events ###
        elif event.event_type == EVENT_WAKE_UP:
            message = '%s wakes up'%event.actor.creature.name
            color = C_MENU
        elif event.event_type == EVENT_NOTICE:
            message = '%s notices you'%event.actor.creature.name
            color = C_MENU
        elif event.event_type == EVENT_STUMBLE:
            if event.actor == self.game.player:
                message = 'You stumble loudly'
                color = C_MENU
        elif event.event_type == EVENT_HEAR:
            if (event.actor == self.game.player and
                event.pos != event.actor.pos):
                direction = util.get_direction(event.actor.x,
                                               event.actor.y,
                                               *event.pos)
                message = 'You hear something to the %s'%direction
                color = C_MENU
                
        elif event.event_type == EVENT_HARVEST:
            message = 'Player harvested a corpse!'
            color = event.majority_material.color
        elif event.event_type == EVENT_HEAL:
            message = 'Player healed %s' % event.part.name
            color = C_EFFECT_MSG

        ### Debug events ###
        elif event.event_type == EVENT_TOGGLE_GHOST:
            message = 'Ghost mode %s' % \
                      ('disabled','enabled')[event.enabled]
            color = C_DEBUG_MSG
        elif event.event_type == EVENT_EXPLORE_EXPLORABLE:
            message = 'Reachable tiles explored'
            color = C_DEBUG_MSG
        elif event.event_type == EVENT_EXPLORE_ALL:
            message = 'Map explored'
            color = C_DEBUG_MSG
        elif event.event_type == EVENT_PRINT_POS:
            message = 'Player at (%i,%i)' % event.thing.pos
            color = C_DEBUG_MSG
        elif event.event_type == EVENT_PRINT_ROOM:
            room = self.game.cur_level.get_room_at(*event.pos)
            if room:
                message = 'In room %i, tags: %s' % \
                          (room.room_id, ', '.join(room.tags))
            else:
                message = 'Not in a room'
            color = C_DEBUG_MSG

        else:
            logger.warning('Failed to handle %s'%event.event_type.upper())

        if message and color:
            message_lines = textwrap.wrap(message, LOG_W-2)
            for line in message_lines:
                self.lines.append((message,color))
            logger.info(message)
            print message

    def render(self,con):
        con.clear()
        con.draw_border(True,C_BORDER,C_BORDER_BKGND)

        for i in range(con.h-2):
            try:
                text, color = self.lines[-(i+1)]
                color = self.make_darker_color(color,i*LOG_FADE/(con.h-3))
                con.set_default_foreground(color)
                con.print_string(1,con.h-2-i,text)
                #for j in range(len(text)):
                #    con.put_char(j+1,con.h-2-i,text[j],color)
            except IndexError:
                pass

    def make_darker_color(self,color,percent):
        if type(percent) == int:
            percent = percent/100
        if percent > 1.0:
            percent = 1.0
        new_r = color['r'] - int(percent*color['r'])
        new_g = color['g'] - int(percent*color['g'])
        new_b = color['b'] - int(percent*color['b'])
        return libtcod.Color(new_r,new_g,new_b)
