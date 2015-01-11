def distance(x1,y1,x2,y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5
def get_direction(x1,y1,x2,y2):
    dx = x1-x2
    dy = y1-y2
    if dx==0:
        if dy>0:
            return 'north'
        else:
            return 'south'
    else:
        ratio=float(dy)/dx
        if ratio >= -0.5 and ratio <= 0.5:
            if dx<0:
                return 'east'
            else:
                return 'west'
        elif ratio <= -2 or ratio >= 2:
            if dy<0:
                return 'south'
            else:
                return 'north'
        elif ratio <= -0.5 and ratio >= -2:
            if dx<0:
                return 'northeast'
            else:
                return 'southwest'
        elif ratio >= 0.5 and ratio <= 2:
            if dx<0:
                return 'southeast'
            else:
                return 'northwest'
