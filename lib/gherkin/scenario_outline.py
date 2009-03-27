#! /usr/bin/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"

import types, re

from peg import Node
from subst_params import subst_params

class ScenarioOutline(Node):
    def __init__(self, **attrs):
        Node.__init__(self, **attrs)
        self.current_example = None
        self.current_row = None
    
    def __call__(self):
        self.kw = 'scenario'
        for ex in self.examples:
            pattern = re.compile(r'<(%s)>' % '|'.join(ex.table.columns))
            self.current_example = ex
           
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
                    step.used_parameters = used
                
                yield self
