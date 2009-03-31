#! /usr/bin/env python

import step_definitions

class ObjectsSpace(object):
    def __init__(self):
        object.__setattr__(self, '__objects', {})
        
    def __getattr__(self, attr):
        def get():
            try:
                return object.__getattribute__(self, '__objects')[attr]
            except KeyError:
                raise AttributeError("object '%s' not exists" % attr)
        return step_definitions.Value(type='callback', value=get)
        
    def __setattr__(self, attr, value):
        object.__getattribute__(self, '__objects')[attr] = value
    
    def __call__(self):
        object.__setattr__(self, '__objects', {})
