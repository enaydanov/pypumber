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
        self.status = None
        self.exception = None
        self.tb = None

    def full_reset(self):
        self.first_run = True
        self.failed = False
        self.reset()

    def run(self, step_definitions):
        EVENT('background', self)
        
        for step in self.steps:
            step.reset()
            step.run(step_definitions)

            if step.exception:
                self.exception = step.exception
                self.tb = step.tb

        if self.first_run:
            if self.exception:
                self.failed = True
            self.first_run = False
        
        self.status = 'done'
        
        EVENT('background', self)
