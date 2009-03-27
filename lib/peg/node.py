#! /usr/lib/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"

class Node(object):
    def __init__(self, **attrs):
        self.__dict__.update(attrs)
    
    def __repr__(self):
        return repr(self.__dict__)
    
    def __contains__(self, attr):
        return hasattr(self, attr)
