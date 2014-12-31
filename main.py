#!/usr/bin/env python2
import libtcodpy as libtcod
import sys, logging, random
from config import *
from game import new_game, load_game

def main_menu():
    return 0

def main():
    logging.basicConfig(filename='log.txt',level=logging.DEBUG,filemode='w')

    logging.debug('start of main')

    #initialize main console
    if EXPERIMENTAL_WALLS:
        font_file = 'data/fonts/arial10x10(new).png'
    else:
        font_file = 'data/fonts/arial10x10.png'
    libtcod.console_set_custom_font(font_file, libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_W,SCREEN_H,'GolemRL')
    libtcod.sys_set_fps(LIMIT_FPS)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_ANY,key,mouse)
        choice = main_menu()
        if choice == 0:
            seed = random.randrange(10000)
            print 'Seed %i'%seed
            logging.info('Starting new game with seed %i' % seed)
            game = new_game()#seed)
            game.play()
        elif choice == 1:
            game = load_game()
            game.play()
        elif choice == 2:
            break

    logging.debug('end of main')
    return 0

if __name__ == ('__main__'):
    main()
