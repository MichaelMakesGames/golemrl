class BodyPartEffect:
    def __init__(self,name,
                 cost, replaces, cancels, removable,
                 health_mod, agility_mod, armor_mod,
                 perception_mod, size_mod, strength_mod):
        self.name = name
        self.cost = cost
        self.cancels = cancels
        self.removable = removable

        self.health_mod = health_mod
        self.agility_mod = agility_mod
        self.armor_mod = armor_mod
        self.perception_mod = perception_mod
        self.size_mod = size_mod
        self.strength_mod = strength_mod
