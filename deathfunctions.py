from config import *

def spawn_animate_clay(game,thing):
    for i in range(game.rng.get_int(2,5)):
        print 'spawning clay %i'%i
        r = 1
        spawned = False
        while not spawned:
            print 'trying in radius %i'%r
            positions = []
            for x in range(thing.x-r,thing.x+r+1):
                positions.append((x, thing.y+r))
                positions.append((x, thing.y-r))
            for y in range(thing.y-r,thing.y+r+1):
                positions.append((thing.x+r, y))
                positions.append((thing.x-r, y))
            j = 0
            while j<len(positions) and not spawned:
                print 'tring tile (%i,%i)'%positions[j]
                t = game.cur_level.get_tile(*positions[j])
                print t.move_through, t.creature
                if t.move_through and not t.creature:
                    game.breeds['ANIMATE_CLAY'].new(positions[j][0],
                                                    positions[j][1],
                                                    game.depth)
                    spawned = True
                j += 1
            r += 1
