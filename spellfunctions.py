from config import *
from event import Event

def get_target_touch(game,caster,direction):
    x = caster.x + direction[0]
    y = caster.y + direction[1]
    target = game.get_creature_at(x,y)
    if target:
        return target
    return False

def get_target_ranged(game,caster,direction):
    hit = False
    x = caster.x
    y = caster.y
    while not hit:
        x += direction[0]
        y += direction[1]
        target = game.get_creature_at(x,y)
        if target:
            hit = True
            return target
        elif not game.cur_level.get_tile(x,y).move_through:
            hit = True
    return False

def heal(game, caster):
    for bp_name in caster.creature.body_parts:
        return caster.creature.body_parts[bp_name].heal(1)

def death_touch(game, caster, direction):
    target = get_target_touch(game, caster, direction)
    if target:
        damage_dealt, killed = target.creature.take_damage(100)
        return caster.notify(Event(EVENT_ATTACK,
                                   actor=caster,
                                   target=target,
                                   hit = True,
                                   dealt = damage_dealt,
                                   killed = killed))
    else:
        return event(EVENT_NONE)

def death_ray(game, caster, direction):
    target = get_target_ranged(game,caster, direction)
    if target:
        damage_dealt, killed = target.creature.take_damage(100)
        return caster.notify(Event(EVENT_ATTACK,
                                   actor=caster,
                                   target=target,
                                   hit = True,
                                   dealt = damage_dealt,
                                   killed = killed))
    else:
        return Event(EVENT_NONE)
