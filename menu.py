from config import *

class Menu:
    def __init__(self, title, options):
        self.title = title
        self.options = options #list of dicts of 'input', 'action', 'name'

        self.action_dict = {1: ACTION_CANCEL_MENU}
        for option in self.options:
            self.action_dict[option['input']] = option['action']

    def render(self,con):
        con.clear()
        con.draw_border(True,C_BORDER,C_BORDER_BKGND)
        con.set_default_foreground(C_MENU)

        y = 2
        for line in self.title.split('\n'):
            x = 2
            for char in line:
                con.put_char(x,y,char)
                x += 1
            y += 1

        y +=2
        for option in self.options:
            x = 2
            option_str = '%s: %s'%(option['input'][0], option['name'])
            for char in option_str:
                con.put_char(x,y,char)
                x += 1
            y += 1
