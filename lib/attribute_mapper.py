#! /usr/bin/env python

import keyword

class AttributeMapper(object):
    def __init__(self, d, cmp=lambda a, b: a == b):
        self.__d = d
        self.__cmp = cmp
    
    def __getattr__(self, attr):
        # E.g.: and_ => and, and__ => and_, etc
        if keyword.iskeyword(attr.rstrip('_')):
            attr = attr[:-1]
        if attr in self.__d:
            return self.__d[attr]
        raise AttributeError()

    def __iter__(self):
        return iter(self.__d)

    def __getitem__(self, key):
        return self.__d[key]

    def __call__(self, value):
        """Find first key for value.
        
        If value not presents, returns None.
        """
        for k, v in self.__d.items():
            if self.__cmp(value, v):
                return k
        else:
            return None
