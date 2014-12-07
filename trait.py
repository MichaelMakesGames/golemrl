class Trait:
    def __init__(self, trait_id, name,
                 applied_to, replaces, cancels,
                 cost, removal_cost, considered,
                 health_mod, agility_mod, armor_mod,
                 perception_mod, size_mod, strength_mod):
        self.trait_id = trait_id
        self.name = name

        self.applied_to = applied_to
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
