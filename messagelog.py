from config import *
import libtcodpy as libtcod
import logging

import textwrap

from observer import Observer

logger = logging.getLogger('message')

class MessageLog(Observer):
    def __init__(self):
        self.lines = []

    def on_notify(self,event):
        message = color = None

        if event.event_type == EVENT_HARVEST:
            message = 'Player harvested a corpse!'
            color = event['majority_material'].written_color

        elif event.event_type == EVENT_TOGGLE_GHOST:
            message = 'Ghost mode %s' % \
                      ('disabled','enabled')[event['enabled']]
            color = C_DEBUG_MSG

        elif event.event_type == EVENT_EXPLORE_EXPLORABLE:
            message = 'Reachable tiles explored'
            color = C_DEBUG_MSG
        elif event.event_type == EVENT_EXPLORE_ALL:
            message = 'Map explored'
            color = C_DEBUG_MSG
        elif event.event_type == EVENT_PRINT_POS:
            message = 'Player at (%i,%i)' % event['thing'].pos
            color = C_DEBUG_MSG
        elif event.event_type == EVENT_PRINT_ROOM:
            room_id = self.owner.cur_level.which_room(*event['pos'])
            if room_id != -1:
                room_tags = self.owner.cur_level.get_room(room_id).tags
                message = 'In room %i, tags: %s' % \
                          (room_id, ', '.join(room_tags))
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
                for j in range(len(text)):
                    con.put_char(j+1,con.h-2-i,text[j],color)
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
