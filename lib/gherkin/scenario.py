#! /usr/bin/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"


from event import EVENT
from peg import Node


class Scenario(Node):
    def __init__(self, **kwargs):
        Node.__init__(self, **kwargs)
        
        self.full_reset()
    
    def reset(self):
        self.status = None
        self.exception = None
        self.traceback = None
    
    def full_reset(self):
        self.reset()
    
    def run(self, step_definitions):
        if step_definitions is not None:
            step_definitions.skip_steps = step_definitions.dry_run
            step_definitions.before()
        
        if self.background:
            self.background.run(step_definitions)
            self.exception = self.background.exception
            self.tb = self.background.tb

        EVENT('scenario', self)

        for step in self.steps:
            step.run(step_definitions)
            if step.exception:
                self.exception = step.exception
                self.tb = step.tb

        self.status = self.exception and 'failed' or 'passed'

        EVENT('scenario', self)

        if step_definitions is not None:
            step_definitions.after()
