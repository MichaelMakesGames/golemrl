from config import *

from event import Event

class BodyPart:
    def __init__(self,name,
                 health,agility,armor,perception,size,strength,
                 vital=False):
        self.name = name
        self.base_max_health = health
        self.health = health
        self.vital = vital
        self.traits = []

        self.base_agility = agility
        self.base_armor = armor
        self.base_perception = perception
        self.base_size = size
        self.base_strength = strength

    @property
    def max_health(self):
        return self.base_max_health + sum([trait.health_mod
                                           for trait in self.traits])

    @property
    def agility(self):
        return self.base_agility + sum([trait.agility_mod
                                        for trait in self.traits])
    @property
    def armor(self):
        return self.base_armor + sum([trait.armor_mod
                                      for trait in self.traits])
    @property
    def perception(self):
        return self.base_perception + sum([trait.perception_mod
                                           for trait in self.traits])
    @property
    def size(self):
        return self.base_size + sum([trait.size_mod
                                     for trait in self.traits])
    @property
    def strength(self):
        return self.base_strength + sum([trait.strength_mod
                                         for trait in self.traits])

    @property
    def intact(self):
        return self.health > 0
    @property
    def damaged(self):
        return self.health < self.max_health

    def take_damage(self,damage_dealt):
        if self.intact:
            damage_received = damage_dealt - self.armor
            if damage_received < 0: damage_received = 0
            self.health -= damage_received
            if self.health <= 0:
                self.health = 0
                return (damage_received, self.vital)
            else:
                return (damage_received, False)
        else:
            return (0,False)

    def can_add(self,trait):
        properly_applied = trait.applied_to in self.name
        requirements_met = (not trait.replaces or
                            trait.replaces in self.traits)

        already_applied = trait in self.traits
        for t in self.traits:
            if t.in_replace_chain(trait):
                already_applied = True

        canceled = False
        for t in self.traits:
            if trait in t.cancels:
                not_canceled = True

        return (properly_applied and
                requirements_met and
                not already_applied and
                not canceled)

    def can_remove(self,trait):
        return (trait in self.traits)

    def add_trait(self,trait,force=False):
        #print 'adding trait'
        if force or self.can_add(trait):
            if trait.replaces:
                self.remove_trait(trait.replaces)
            self.traits.append(trait)
            self.health += trait.health_mod
            return self.owner.owner.notify(Event(EVENT_ADD_TRAIT,
                                                 actor=self.owner.owner,
                                                 body_part=self,
                                                 trait=trait) )
        else: return Event(EVENT_NONE)

    def remove_trait(self,trait,force=False):
        if force or self.can_remove(trait):
            if trait.replaces:
                self.add_trait(trait.replaces, True)
            self.traits.remove(trait)
            self.health -= trait.health_mod
