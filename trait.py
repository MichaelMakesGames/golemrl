class Trait:
    def __init__(self, trait_id, name, applied_to,
                 prefix=None, suffix=None,
                 replaces=None, cancels=[],
                 cost={}, removal_cost={}, considered='neutral',
                 health_mod=0, agility_mod=0, armor_mod=0,
                 perception_mod=0, size_mod=0, strength_mod=0):
        self.trait_id = trait_id
        self.name = name
        self.applied_to = applied_to

        self.prefix = prefix
        self.suffix = suffix

        self.replaces = replaces
        self.cancels = cancels

        self.cost = cost
        self.removal_cost = removal_cost
        self.considered = considered

        self.health_mod = health_mod
        self.agility_mod = agility_mod
        self.armor_mod = armor_mod
        self.perception_mod = perception_mod
        self.size_mod = size_mod
        self.strength_mod = strength_mod

    @property
    def removable(self):
        return bool(self.removal_cost)

    def in_replace_chain(self,trait):
        if self.replaces == None:
            return False
        elif self.replaces == trait:
            return True
        else:
            return self.replaces.in_replace_chain(trait)
