#! /usr/bin/env python

import copy

class Options(object):
    def __init__(self, **defaults):
        self.opts = copy.copy(defaults)
    
    def __getattr__(self, attr):
        if attr in self.opts:
            return self.opts[attr]
        raise AttributeError
