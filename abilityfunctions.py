from config import *
import math
from event import Event

def heal_trigger(game,ability,event):
    event_type = event.event_type
    if (event_type == EVENT_ACTIVATE and
        event.ability == ability and
        ability in event.actor.creature.abilities):
        return True
    else:
        return False
def heal_effect(game,ability,event):
    actor = event.actor
    for bp_name in actor.creature.body_parts:
        bp = actor.creature.body_parts[bp_name]
        if bp.health < bp.max_health:
            bp.heal(math.ceil((bp.max_health-bp.health)/2.0))
    return Event(EVENT_USE,actor=actor,ability=ability)
    
def charge_trigger(game,ability,event):
    event_type = event.event_type
    if (event_type == EVENT_ACTIVATE and
        event.ability == ability and
        ability in event.actor.creature.abilities):
        return True
    return False
def charge_effect(game,ability,event):
    event.actor.creature.add_ability('CHARGE_1')
    game.input_state = INPUT_DIRECTION_8
    return Event(EVENT_NONE)

def charge_1_trigger(game,ability,event):
    event_type = event.event_type
    if (event_type==EVENT_DIRECTION and
        ability in event.actor.creature.abilities):
        game.input_state = INPUT_NORMAL
        return True
    elif (event_type==EVENT_CANCEL):
        game.input_state = INPUT_NORMAL
        return False
    else:
        return False
def charge_1_effect(game,ability,event):
    actor = event.actor
    direction = event.direction
    actor.creature.remove_ability(ability)
    first_tile  = game.cur_level.get_tile(actor.x+direction[0],
                                          actor.y+direction[1])
    second_tile = game.cur_level.get_tile(actor.x+direction[0]*2,
                                          actor.y+direction[1]*2)
    movement_event = actor.move_or_attack(*direction)
    if movement_event.event_type == EVENT_MOVE:
        if second_tile.creature:
            actor.creature.add_status_effect('OFF_BALANCE')
            actor.creature.add_status_effect('CHARGING')
            actor.creature.attack(second_tile.creature)
            actor.creature.remove_status_effect('CHARGING')

    return movement_event

def dodge_trigger(game,ability,event):
    event_type = event.event_type
    if (event_type == EVENT_ACTIVATE and
        event.ability == ability and
        ability in event.actor.creature.abilities):
        print 'dodge triggered'
        return True
    else:
        return False
def dodge_effect(game,ability,event):
    print 'in dodge_effect'
    actor = event.actor
    actor.creature.add_status_effect('DODGING')
    actor.creature.add_ability('DODGE_1')
    actor.creature.add_ability('DODGE_1_ALT')
    return Event(EVENT_USE,actor=actor,ability=ability)
def dodge_1_trigger(game,ability,event):
    event_type = event.event_type
    if (event_type == EVENT_ATTACK and
        ability in event.target.creature.abilities and
        event.hit == False):
        print 'dodge 1 triggered'
        return True
    return False
def dodge_1_effect(game,ability,event):
    print 'in dodge_1_effect'
    event.target.creature.remove_status_effect('DODGING')
    event.target.creature.remove_ability(ability)
    event.target.creature.remove_ability('DODGE_1_ALT')
    if event.hit == False:
        event.target.creature.add_ability('DODGE_2')
        game.input_state = INPUT_DIRECTION_8
        return Event(EVENT_NONE)
    else:
        return Event(EVENT_NONE)

def dodge_1_alt_trigger(game,ability,event):
    event_type = event.event_type
    if (event_type == EVENT_ATTACK and
        ability in event.target.creature.abilities and
        event.hit == True):
        print 'dodge 1 alt triggered'
        return True
    elif ((event_type==EVENT_MOVE or
           event_type==EVENT_ATTACK) and
          ability in event.actor.creature.abilities):
        return True
def dodge_1_alt_effect(game,ability,event):
    if (event.event_type == EVENT_ATTACK and
        ability in event.target.creature.abilities):
        dodger = event.target
    else:
        dodger = event.actor
    dodger.creature.remove_status_effect('DODGING')
    dodger.creature.remove_ability(ability)
    dodger.creature.remove_ability('DODGE_1')
    return Event(EVENT_NONE)

def dodge_2_trigger(game,ability,event):
    event_type = event.event_type
    if (event_type == EVENT_DIRECTION and
        ability in event.actor.creature.abilities):
        print 'dodge 2 triggered'
        return True
    return False
def dodge_2_effect(game,ability,event):
    print 'in dodge_2_effect'
    actor = event.actor
    movement_event = actor.move_to(actor.x+event.direction[0],
                                   actor.y+event.direction[1])
    if movement_event.event_type == EVENT_MOVE:
        actor.creature.remove_ability(ability)
        game.input_state = INPUT_NORMAL
    return movement_event
'''
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
            return actor.creature.attack(second_tile.creature,
                                         degree_mod=1,
                                         sound_multiplier=3)
    return movement_event

def tackle(game, actor, direction):
    target = get_target_touch(game,actor,direction)
    if target:
        degree = (actor.creature.size//20 + game.rng.roll(actor.creature.strength,6) > target.creature.size//20 + game.rng.roll(actor.creature.strength,6)) // DEGREE_OF_SUCCESS + 1
        push_to = game.cur_level.get_tile(actor.x+2*direction[0],
                                          actor.y+2*direction[1])
        if degree>0:
            target.creature.losing_balance=True
            if (game.rng.percent(degree*100/2) and
                push_to.move_through and
                push_to.creature==None):
                target.move_to(actor.x+2*direction[0],
                               actor.y+2*direction[1])
                actor.move_to(actor.x+direction[0],
                              actor.y+direction[1])
                
        elif degree<0:
            actor.losing_balance=True
    return Event(EVENT_NONE)
            

def defensive_stance(game, actor, bp): pass
def dodge(game, actor): pass

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
'''
