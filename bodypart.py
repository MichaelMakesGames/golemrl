class BodyPart:
    def __init__(self,name,
                 health,agility,armor,perception,size,strength,
                 vital=False):
        self.name = name
        self.base_max_health = health
        self.health = health
        self.vital = vital
        self.effects = []

        self.base_agility = agility
        self.base_armor = armor
        self.base_perception = perception
        self.base_size = size
        self.base_strength = strength

    @property
    def max_health(self):
        return self.base_max_health + sum([effect.health_mod
                                           for effect in self.effects])

    @property
    def agility(self):
        return self.base_agility + sum([effect.agility_mod
                                        for effect in self.effects])
    @property
    def armor(self):
        return self.base_armor + sum([effect.armor_mod
                                      for effect in self.effects])
    @property
    def perception(self):
        return self.base_perception + sum([effect.perception_mod
                                           for effect in self.effects])
    @property
    def size(self):
        return self.base_size + sum([effect.size_mod
                                     for effect in self.effects])
    @property
    def strength(self):
        return self.base_strength + sum([effect.strength_mod
                                         for effect in self.effects])

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

    def add_effect(self,effect):
        self.effects.append(effect)
        self.health += effect.health_mod
