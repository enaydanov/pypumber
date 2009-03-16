#! /usr/bin/env python

"""Implementation of Singleton pattern.

Example:
    >>> @singleton
    >>> class SomeClass(Singleton):
    >>>   def __init__(self):
    >>>     print "aaa"
    >>> a = SomeClass()
    aaa
    
    >>> b = SomeClass()
    >>> a is b
    True
    
"""

def singleton(cls):
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance
