#! /usr/bin/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"

import multiplexer

EVENT = multiplexer.Multiplexer()

def add_listener(listener):
    EVENT.__outputs__.append(listener)
