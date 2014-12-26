from config import *
from event import Event

def heal(game, caster):
    if caster == game.player:
        for bp_name in caster.creature.body_parts:
            caster.creature.body_parts[bp_name].heal(1)
    else:
        caster.creature.heal(1)

def death_touch(game, caster, direction):
    target_x = caster.x + direction[0]
    target_y = caster.y + direction[1]
    targets = game.get_things_at(target_x,target_y)
    for target in targets:
        if target.creature and target.creature.alive:
            damage_dealt, killed = target.creature.take_damage(100)
            return caster.notify(Event(EVENT_ATTACK,
                                       actor=caster,
                                       target=target,
                                       hit = True,
                                       dealt = damage_dealt,
                                       killed = killed))

def death_ray(game, caster, direction):
    hit_something = False
    x,y = caster.x, caster.y
    while not hit_something:
        x += direction[0]
        y += direction[1]
        targets = game.get_things_at(x,y)
        print 'checking tile',x,y,game.cur_level.get_tile(x,y).move_through
        for target in targets:
            if target.creature and target.creature.alive:
                hit_something = True
                damage_dealt, killed = target.creature.take_damage(100)
                return caster.notify(Event(EVENT_ATTACK,
                                           actor=caster,
                                           target=target,
                                           hit = True,
                                           dealt = damage_dealt,
                                           killed = killed))
        if not game.cur_level.get_tile(x,y).move_through:
            hit_something = True
