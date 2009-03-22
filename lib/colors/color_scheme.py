#! /usr/bin/env python

class ColorScheme(object):
    def __init__(self, color_scheme, color_string=lambda c, s: s, output=None):
        self.color_scheme = color_scheme
        self.color_string = color_string
        if output is None:
            self.write = lambda str: str
        else:
            self.write = output.write
    
    def __getattr__(self, attr):
        if attr in self.color_scheme:
            return lambda str: \
                self.write(
                    self.color_string(self.color_scheme[attr], str)
                )
        else:
            raise AttributeError("ColorScheme: color for '%s' is undefined." % attr)
