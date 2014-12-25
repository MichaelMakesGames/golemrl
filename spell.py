from config import *

class Spell:
    def __init__(self, spell_id, name, func, targeting='self', desc='', cost={}, requires=[None,None]):
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
        if self.targeting == 'self':
            self.func(self.owner,caster)
    def can_cast(self,caster):
        if self.requires[0] == None:
            return True
        for bp_name in caster.creature.body_parts:
            if self.requires[0] in bp_name:
                if caster.creature.body_parts[bp_name].has_word(self.requires[1]):
                    return True
        return False
