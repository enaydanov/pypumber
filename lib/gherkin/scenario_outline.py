#! /usr/bin/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"

import types, re

from peg import Node
from event import EVENT
from subst_params import subst_params
from scenario import Scenario


class ScenarioOutline(Scenario):
    def __init__(self, **attrs):
        Scenario.__init__(self, **attrs)
        
        self.full_reset()

    def reset(self):
        Scenario.reset(self)
        self.current_columns = None
        self.current_widths = None
        self.current_row = None
    
    def full_reset(self):
        Scenario.full_reset(self)
    
    def run(self, step_definitions):
        EVENT('scenario_outline', self)
        
        Scenario.run(self, None)

        for ex in self.examples:
            EVENT('examples', ex)
            
            pattern = re.compile(r'<(%s)>' % '|'.join(ex.table.columns))
            self.current_columns = ex.table.columns
            self.current_widths = ex.table.widths
           
            for values in ex.table.rows:
                self.current_row = values
                # Substitute outline parameters.
                for step in self.steps:
                    step.name, used = subst_params(step.name_template, pattern, values)
                    if step.multi is not None:
                        if type(step.multi) == types.StringType:
                            # PyString
                            step.multi, used_in_multi = subst_params(step.multi_template, pattern, values)
                        else:
                            # Table
                            used_in_multi = step.multi.subst(pattern, values)
                        used |= used_in_multi
                    step.full_reset()
                    step.used_parameters = used
                Scenario.reset(self)
                Scenario.run(self, step_definitions)

        self.status = 'done'
        self.exception = None
        self.tb = None
        
        EVENT('scenario_outline', self)
