import libtcodpy as libtcod
import logging
from config import *

class Console:
    def __init__(self,title,x,y,w,h):
        self.title = title
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.con = libtcod.console_new(w,h)

    def set_default_foreground(self,color):
        libtcod.console_set_default_foreground(self.con,color)

    def set_default_background(self,color):
        libtcod.console_set_default_background(self.con,color)

    def put_char(self,x,y,char,color=None,bkgnd=None):
        libtcod.console_put_char(self.con,x,y,char,libtcod.BKGND_NONE)
        if color:
            self.set_char_foreground(x,y,color)
        if bkgnd:
            self.set_char_background(x,y,bkgnd)

    def set_char_background(self,x,y,color):
        libtcod.console_set_char_background(self.con,x,y,color)

    def set_char_foreground(self,x,y,color):
        libtcod.console_set_char_foreground(self.con,x,y,color)

    def put_char_ex(self,x,y,char,color,bkgnd):
        libtcod.console_put_char_ex(self.con,x,y,char,color,bkgnd)

    def get_background_flag(self):
        return libtcod.console_get_background_flag(self.con)
    def set_alignment(self, alignment):
        libtcod.console_set_alignment(self.con, alignment)
    def get_alignment(self, alignment):
        return libtcod.console_get_alignment(self.con)
    def print_string(self, x, y, s, alignment=None, bkgnd_flag=None):
        if alignment or bkgnd_flag:
            if not alignment: alignment = self.get_alignment()
            if not bkgnd_flag: bkgnd_flag = self.get_background_flag()
            libtcod.console_print_ex(self.con,x,y,bkgnd_flag,alignment,s)
        else:
            libtcod.console_print(self.con,x,y,s)

    def blit(self):
        libtcod.console_blit(self.con,0,0,self.w,self.h,0,self.x,self.y)

    def clear(self,foreground=libtcod.black,background=libtcod.black):
        self.set_default_foreground(foreground)
        self.set_default_background(background)
        libtcod.console_clear(self.con)

    def draw_border(self,draw_title=True,color=libtcod.white,bkgnd=libtcod.black):
        for i in range(self.w):
            self.put_char_ex(i,0,libtcod.CHAR_HLINE,color,bkgnd)
            self.put_char_ex(i,self.h-1,libtcod.CHAR_HLINE,color,bkgnd)
        for i in range(self.h):
            self.put_char_ex(0,i,libtcod.CHAR_VLINE,color,bkgnd)
            self.put_char_ex(self.w-1,i,libtcod.CHAR_VLINE,color,bkgnd)

        self.put_char_ex(0,0,libtcod.CHAR_NW,color,bkgnd)
        self.put_char_ex(0,self.h-1,libtcod.CHAR_SW,color,bkgnd)
        self.put_char(self.w-1,0,libtcod.CHAR_NE,color,bkgnd)
        self.put_char(self.w-1,self.h-1,libtcod.CHAR_SE,color,bkgnd)

        if draw_title:
            x = 1
            for char in self.title:
                if x < self.w - 1 and char != ' ':
                    self.put_char_ex(x,0,char,color,bkgnd)
                x += 1
