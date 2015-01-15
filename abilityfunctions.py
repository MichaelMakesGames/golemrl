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

def charge(game, actor, direction):
    first_tile  = game.cur_level.get_tile(actor.x+direction[0],
                                          actor.y+direction[1])
    second_tile = game.cur_level.get_tile(actor.x+direction[0]*2,
                                          actor.y+direction[1]*2)
    movement_event = actor.move_or_attack(*direction)
    if movement_event.event_type == EVENT_MOVE:
        if second_tile.creature:
            actor.creature.losing_balance=True
            return actor.creature.attack(second_tile.creature,1)
    return movement_event

def heal(game, caster):
    for bp_name in caster.creature.body_parts:
        caster.creature.body_parts[bp_name].heal(1)

def death_touch(game, caster, direction):
    target = get_target_touch(game, caster, direction)
    if target:
        damage_dealt, killed = target.creature.take_damage(100,100)
        return caster.notify(Event(EVENT_ATTACK,
                                   actor=caster,
                                   target=target,
                                   hit = True,
                                   degree = 100,
                                   dealt = damage_dealt,
                                   killed = killed))
    else:
        return Event(EVENT_NONE)

def death_ray(game, caster, direction):
    target = get_target_ranged(game,caster, direction)
    if target:
        damage_dealt, killed = target.creature.take_damage(100,100)
        return caster.notify(Event(EVENT_ATTACK,
                                   actor=caster,
                                   target=target,
                                   degree=100,
                                   hit = True,
                                   dealt = damage_dealt,
                                   killed = killed))
    else:
        return Event(EVENT_NONE)
