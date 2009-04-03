#! /usr/bin/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"


from event import EVENT
from peg import Node


class Background(Node):
    def __init__(self, **kwargs):
        Node.__init__(self, **kwargs)

        self.full_reset()
    
    def reset(self):
        self.exception = None
        self.tb = None

    def full_reset(self):
        self.first_run = True
        self.reset()

    def run(self, step_definitions):
        EVENT('background', self)
        
        for step in self.steps:
            step.run(step_definitions)
            
            if step.exception:
                self.exception = step.exception
                self.tb = step.tb

        self.first_run = False
