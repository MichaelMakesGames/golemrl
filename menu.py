from config import *

class Menu:
    def __init__(self, title, options):
        self.title = title
        self.options = options #list of dicts of 'input', 'action', 'name'

        self.action_dict = {('q',False): ACTION_CANCEL_MENU}
        for option in self.options:
            self.action_dict[option['input']] = option['action']

    def render(self,con):
        con.clear()
        con.draw_border(True,C_BORDER,C_BORDER_BKGND)
        
        y = 2
        x = 2
        for char in self.title:
            con.put_char(x,y,char,libtcod.white)
            x += 1

        y = 4
        for option in self.options:
            x = 2
            option_str = '%s: %s'%(option['input'][0], option['name'])
            for char in option_str:
                con.put_char(x,y,char,libtcod.white)
                x += 1
            y += 1
