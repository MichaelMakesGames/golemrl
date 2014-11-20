import libtcodpy as libtcod

class Dice:
    def __init__(self,number,sides,rng=0):
        self.number = number
        self.sides = sides
        self.rng = rng

    @property
    def average(self):
        return self.number * (self.sides+1) / 2.0

    def roll(self):
        return sum([libtcod.random_get_int(self.rng,1,self.sides)
                    for i in range(self.number)])

    def __repr__(self):
        return "%id%i" % (self.number, self.sides)
