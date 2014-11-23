import libtcodpy as libtcod

class RNG:
    def __init__(self,rng=None,seed=None):
        if seed == None and rng == None:
            self.rng = 0
        elif rng:
            self.rng = rng
        elif seed:
            self.rng = libtcod.random_new_from_seed(seed)

    def get_float(self,minimum,maximum):
        return libtcod.random_get_float(self.rng,minimum,maximum)

    def get_int(self,minimum,maximum):
        return libtcod.random_get_int(self.rng,minimum,maximum-1)

    def roll(self,num_dice,num_sides):
        return sum( [self.get_int(1,num_sides+1)
                     for i in range(num_dice)] )

    def choose(self,sequence):
        return sequence[ self.get_int(0,len(sequence)) ]

    def choose_weighted(self, sequence, key = lambda i: i.weight ):
        cur_item = 0
        cur_weight = 0
        total_weight = sum([key(i) for i in sequence])
        choice = self.get_int(0,total_weight)
        while True:
            cur_weight += key(sequence[cur_item])
            if choice < cur_weight:
                return sequence[cur_item]
            cur_item += 1

    def delete(self):
        libtcod.random_delete(self.rng)
