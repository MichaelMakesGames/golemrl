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
        if target.creature:
            damage_dealt, killed = target.creature.take_damage(100)
            return caster.notify(Event(EVENT_ATTACK,
                                       actor=caster,
                                       target=target,
                                       hit = True,
                                       dealt = damage_dealt,
                                       killed = killed))
