#! /usr/bin/env python

import sys

ATTRIBUTES = {
    'reset':  0,
    'bold':  1,
    'dark': 2,
    'italic': 3, # not widely implemented
    'underline': 4,
    'underscore': 4, # synonym for':underline
    'blink': 5,
    'rapid_blink': 6, # not widely implemented
    'negative': 7, # no reverse because of String#reverse
    'concealed': 8,
    'strikethrough': 9, # not widely implemented
    'black': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
    'on_black': 40,
    'on_red': 41,
    'on_green': 42,
    'on_yellow': 43,
    'on_blue': 44,
    'on_magenta': 45,
    'on_cyan': 46,
    'on_white': 47,
}

def color(*args):
    return tuple([ATTRIBUTES[a] for a in args])

DEFAULT_COLORS = {
    'undefined':  	color('yellow'),
    'pending': 	color('yellow'),
    'pending_param': 	color('yellow', 'bold'),
    'failed': 	color('red'),
    'failed_param': 	color('red', 'bold'),
    'passed': 	color('green'),
    'passed_param': 	color('green', 'bold'),
    'skipped': color('cyan'),
    'skipped_param': color('cyan', 'bold'),
    'comment': color('white', 'bold'),
    'tag': color('cyan'),
}

def color_to_seq(c):
    return '\033[%sm' % ';'.join(['%d' % attr in c])

def color_string(color, str):
    return ''.join([color_to_seq(color), str, '\033[m'])
