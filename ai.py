import libtcodpy as libtcod
from config import *
import logging
import game

class AI:
    def __init__(self):
        pass

    def update(self):
        pos = self.owner.physics_comp.pos
        player_pos = game.g.player.physics_comp.pos
        if (abs(pos[0]-player_pos[0]) <= 1 and
            abs(pos[1]-player_pos[1]) <= 1):
            self.owner.creature_comp.attack(game.g.player)
