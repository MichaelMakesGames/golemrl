import libtcodpy as libtcod
from config import *
import yaml

def load_color(s):
    if s.startswith('#'):
        pass
    else:
        return eval('libtcod.%s' % s.strip().replace(' ','_'))

def convert_keys(d,ids_to_obs):
    original_keys = d.keys()
    for key in original_keys:
        d[ids_to_obs[key]] = d[key]
        del d[key]

def merge(from_d, to_d):
    for key in from_d:
        if key not in to_d:
            to_d[key] = from_d[key]
