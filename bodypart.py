from config import *

from event import Event

class BodyPart:
    def __init__(self,golem,name,
                 word_slots,
                 health,agility,armor,perception,size,strength,
                 vital=False,
                 traits=[]):
        self.golem = golem
        self.name = name
        self.base_max_health = health
        self.health = health
        self.vital = vital
        self.traits = traits
        self.words = [None for i in range(word_slots)]

        self.base_word_slots = word_slots
        self.base_agility = agility
        self.base_armor = armor
        self.base_perception = perception
        self.base_size = size
        self.base_strength = strength

    @property
    def thing(self):
        return self.golem.owner
    @property
    def game(self):
        return self.thing.game

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
    def word_slots(self):
        slots = self.base_word_slots + sum([trait.word_slots_mod
                                            for trait in self.traits])
        return max(0,slots)


    @property
    def full_name(self):
        full_name = self.name
        for trait in self.traits:
            if trait.prefix:
                full_name = trait.prefix + ' ' + full_name
            if trait.suffix:
                full_name = full_name + ' ' + trait.suffix
        return full_name

    @property
    def intact(self):
        return self.health > 0
    @property
    def damaged(self):
        return self.health < self.max_health

    def take_damage(self,damage_dealt,degree):
        if self.intact:
            damage_received = damage_dealt*degree - self.armor
            if damage_received < 0: damage_received = 0
            self.health -= damage_received
            if self.health <= 0:
                self.health = 0
                return (damage_received, self.vital)
            else:
                return (damage_received, False)
        else:
            return (0,False)

    def heal(self,amount):
        if self.health+amount <= self.max_health:
            self.health += amount

    def check_word_slots(self):
        while self.word_slots > len(self.words):
            self.words.append(None)
        while self.word_slots < len(self.words):
            if None in self.words:
                self.words.remove(None)
            else:
                self.erase(self.game.rng.choose(self.words))

    def inscribe(self,word):
        if word not in self.words and None in self.words:
            self.words[self.words.index(None)] = word
            return self.thing.notify(Event(EVENT_INSCRIBE,
                                           actor = self.thing,
                                           body_part = self,
                                           word = word))

    def erase(self,word):
        if word in self.words:
            self.words[self.words.index(word)] = None
            return self.thing.notify(Event(EVENT_ERASE,
                                           actor = self.thing,
                                           body_part = self,
                                           word = word))

    def has_word(self,word):
        return word in self.words

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
                not canceled and
                trait.cost != None)

    def can_remove(self,trait):
        return (trait in self.traits and
                trait.removal_cost != None)

    def add_trait(self,trait,force=False):
        if force or self.can_add(trait):
            if trait.replaces:
                self.remove_trait(trait.replaces)
            self.traits.append(trait)
            self.health += trait.health_mod
            self.check_word_slots()
            if not force: #WARNING, this might cause trouble, but for now it seems like we're best not raising an event when we force a trait (ie player starting traits, and a trait that's added as a result of trait that replaced it being removed
                return self.thing.notify(Event(EVENT_ADD_TRAIT,
                                               actor=self.thing,
                                               body_part=self,
                                               trait=trait) )
        else: return Event(EVENT_NONE)

    def remove_trait(self,trait,force=False):
        if force or self.can_remove(trait):
            if trait.replaces:
                self.add_trait(trait.replaces, True)
            self.traits.remove(trait)
            self.health -= trait.health_mod
            self.check_word_slots()
            if not force:
                return self.thing.notify(Event(EVENT_REMOVE_TRAIT,
                                               actor = self.thing,
                                               body_part = self,
                                               trait = trait))
