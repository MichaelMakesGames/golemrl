#!/usr/bin/env python2
import libtcodpy as libtcod
import sys, logging, random
from config import *
import game
#from game import new_game, load_game, g

def main_menu():
    return 0

def main():
    logging.basicConfig(filename='log.txt',level=logging.DEBUG,filemode='w')

    logging.debug('start of main')

    #initialize main console
    libtcod.console_set_custom_font('data/arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_W,SCREEN_H,'GolemRL')
    libtcod.sys_set_fps(LIMIT_FPS)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_ANY,key,mouse)
        choice = main_menu()
        if choice == 0:
            seed = random.randrange(10000)
            print seed
            game.new_game()#seed)
            game.g.play()
        elif choice == 1:
            load_game()
            game.g.play()
        elif choice == 2:
            break

    logging.debug('end of main')
    return 0

if __name__ == ('__main__'):
    main()
