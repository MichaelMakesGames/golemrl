from config import *

from event import Event

class Ability:
    def __init__(self, game, ability_id, name, ability_type, func, targeting='self', desc='', initiate_text='', activate_text='', cost={}, requires=[None,None]):
        self.game = game
        self.ability_id = ability_id
        self.name = name
        self.ability_type = ability_type
        self.targeting = targeting
        self.desc = desc
        self.initiate_text = initiate_text
        self.activate_text = activate_text
        self.cost = cost
        self.requires = requires
        self.func = func

    @property
    def word(self):
        return self.requires[1]

    def activate(self,actor,direction=None):
        #Notify event first so message about ability
        #is printed before messages about the outcome
        event = actor.notify(Event(EVENT_ACTIVATE_ABILITY,
                                   actor = actor,
                                   ability = self))
        if self.targeting == 'self':
            self.func(self.game,actor)
        if self.targeting in ['touch','ranged','other']:
            self.func(self.game,actor,direction)
        return event

    def can_activate(self,actor):
        if self.requires[0] == None:
            return True
        for bp_name in actor.creature.body_parts:
            if self.requires[0] in bp_name:
                if actor.creature.body_parts[bp_name].has_word(self.requires[1]):
                    return True
        return False
