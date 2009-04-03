#! /usr/lib/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"

import copy

class Node(object):
    def __init__(self, **attrs):
        self.__dict__.update(attrs)
        self.__backup__ = copy.copy(self.__dict__)
    
    def __repr__(self):
        return repr(self.__dict__)
    
    def __contains__(self, attr):
        return hasattr(self, attr)
