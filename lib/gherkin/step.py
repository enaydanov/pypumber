#! /usr/bin/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"

import sys

from step_definitions import StepSkipped, Undefined, Pending
from event import EVENT
from peg import Node


class Step(Node):
    def __init__(self, **kwargs):
        Node.__init__(self, **kwargs)
        
        self.full_reset()
    
    def reset(self):
        self.status = None
        self.exception = None
        self.tb = None
    
    def full_reset(self):
        self.match = None
        self.reset()
        
    def run(self, step_definitions=None):
        EVENT('step', self)
        
        if self.status is not None:
            return

        if step_definitions is None:
            self.status = 'outline'
        else:
            try:
                if self.match is None:
                    self.match = getattr(step_definitions, self.section)(self.name, self.multi)
                self.match()
                self.status = 'passed'
            except StepSkipped:
                self.status = 'skipped'
            except Undefined, self.exception:
                self.status = 'undefined'
            except Pending, self.exception:
                self.status = 'pending'
            except Exception, self.exception:
                self.status = 'failed'
            
            if self.exception:
                self.tb = sys.exc_info()[2]

            step_definitions.skip_steps |= bool(self.exception)
            
        EVENT('step', self)
