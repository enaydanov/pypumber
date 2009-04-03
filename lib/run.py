#! /usr/bin/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"


from cfg.set_defaults import set_defaults
from event import EVENT

class Run(object):
    def __init__(self):
        set_defaults(self, 'scenario_names', 'tags')
        self.status = None

    def __call__(self, features, step_definitions):
        EVENT('run', self)
        
        for filename, feat, lines in features:
            feat.filename = filename
            feat.run(step_definitions, self.tags, self.scenario_names or None, lines)
        
        self.status = 'done'
        
        EVENT('run', self)
