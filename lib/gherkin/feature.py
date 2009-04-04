#! /usr/bin/env python

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"


from event import EVENT
from peg import Node


class Feature(Node):
    def __init__(self, **kwargs):
        Node.__init__(self, **kwargs)
        
        self.status = None
    
    def run(self, step_definitions, tags=None, scenario_names=None, lines=None):
        EVENT('feature', self)

        if tags is not None:
            positive_tags = set([tag for tag in tags if tag[0] != '~'])
            negative_tags = set([tag[1:] for tag in tags if tag[0] == '~'])
        
        for sc in self.feature_elements:
            # Skip scenario by line number.
            if (lines is not None) and (sc.lineno not in lines):
                continue
                
            # Skip scenario by name.
            if (scenario_names is not None) and (sc.name not in scenario_names):
                continue
                
            # Skip scenario by tags.
            if tags is not None:
                _tags = self.tags | sc.tags
                if (negative_tags & _tags) or not (positive_tags & _tags):
                    continue

            for scenario in sc:
                if step_definitions:
                    step_definitions.skip_steps = step_definitions.dry_run
                    step_definitions.skip_steps |= bool(self.background) and self.background.failed
                        
                skip_before_after = not bool(step_definitions) or step_definitions.skip_steps
                
                #
                # Run sequence: Before -> Background -> Scenario -> After
                #
                if not skip_before_after:
                    step_definitions.before()
                   
                if self.background:
                    self.background.run(step_definitions)
                    skip_before_after |= self.background.failed
                
                scenario.run(step_definitions)
                
                if not skip_before_after:
                    step_definitions.after()

                # Prepare background for next scenario.
                if self.background:
                    self.background.reset()

        self.status = 'done'
        
        EVENT('feature', self)
