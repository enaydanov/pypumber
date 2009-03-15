#! /usr/bin/env python

class _Self(object):
    def __init__(self, lst):
        self._lst = lst
        
    def __getattribute__(self, attr):
        if attr == '_lst':
            return object.__getattribute__(self, attr)
        return list.__getattribute__(self._lst, attr)

class Multiplexor(list):
    def __init__(self, *objs):
        slf = self.__self__
        for obj in objs:
            slf.append(obj)
    
    def __getattribute__(self, attr):
        if attr == '__self__':
            return _Self(self)
        raise AttributeError()
    
    def __getattr__(self, attr):
        return Multiplexor(*[getattr(obj, attr) for obj in self])

    def __setattr__(self, attr, value):
        for obj in self:
            setattr(obj, attr, value)
    
    def __delattr__(self, attr):
        for obj in self:
            delattr(obj, attr)

    def __getitem__(self, key):
        return Multiplexor(*[obj[key] for obj in self])

    def __setitem__(self, key, value):
        for obj in self:
            obj[key] = value
    
    def __delitem__(self, key):
        for obj in self:
            del(obj[key])
        
    def __call__(self, *args, **kwargs):
        for obj in self:
            obj(*args, **kwargs)
