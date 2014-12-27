from config import *

from event import Event

class Spell:
    def __init__(self, game, spell_id, name, func, targeting='self', desc='', cost={}, requires=[None,None]):
        self.game = game
        self.spell_id = spell_id
        self.name = name
        self.targeting = targeting
        self.desc = desc
        self.cost = cost
        self.requires = requires
        self.func = func

    @property
    def word(self):
        return self.requires[1]

    def cast(self,caster,direction=None):
        #Notify event first so message about spell
        #is printed before messages about the outcome
        event = caster.notify(Event(EVENT_CAST_SPELL,
                                    actor = caster,
                                    spell = self))
        if self.targeting == 'self':
            self.func(self.game,caster)
        if self.targeting == 'touch' or self.targeting == 'ranged':
            self.func(self.game,caster,direction)
        return event

    def can_cast(self,caster):
        if self.requires[0] == None:
            return True
        for bp_name in caster.creature.body_parts:
            if self.requires[0] in bp_name:
                if caster.creature.body_parts[bp_name].has_word(self.requires[1]):
                    return True
        return False
