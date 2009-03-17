#! /usr/bin/en python

import sys

if sys.platform == 'win32':
    def set_color():
        pass
    
    def get_color():
        pass
else:
        def set_color():
        pass
    
    def reset_color():
        pass


def color_output(color, s, out=sys.stdout):
    c = get_color()
    set_color(color)
    out.write(s)
    set_color(c)
    
    
