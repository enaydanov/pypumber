#! /usr/bin/env python

from cfg.set_defaults import set_defaults
from pprint import pprint

class ButFailed(Exception):
    pass

class SkipStep(Exception):
    pass

class Run(object):
    def __init__(self):
        set_defaults(self, 'scenario_names', 'tags')

    def skip_feature_by_tags(self, tags):
        self._run_whole_feature = False
        if self.tags is None or tags == []:
            return False
        for tag in self.tags:
            if tag[0] == '~':
                if tag[1:] in tags:
                    return True
            elif tag in tags:
                self._run_whole_feature = True # side-effect
                return False
        return False

    def skip_scenario_by_tags(self, tags):
        if self.tags is None:
            return False
        skip = not self._run_whole_feature
        for tag in self.tags:
            if tag[0] == '~':
                if tag[1:] in tags:
                    return True
            else:
                if tag in tags:
                    skip = False
        return skip

    def skip_scenario_by_name(self, name):
        return (self.scenario_names != []) and (name not in self.scenario_names)


    def _run_steps(self, steps, step_definitions, context):
        current_kw = None
        for step in steps:
            kw = step.step_keyword[0]
            if kw in ['given', 'when', 'then']:
                current_kw = kw
            else:
                if current_kw is None:
                    raise SyntaxError()
            with context.step(current_kw, step) as step_context:
                match = getattr(step_definitions, current_kw)(step.name)
                if step_context is not None:
                    step_context.matchobj = match.matchobj
                    step_context.fn = match.fn
                if context.skip_following_steps:
                    raise SkipStep()
                if kw == 'but':
                    try:
                        match()
                    except: # Do we need to catch all other exceptions? 
                        pass
                    else:
                        raise ButFailed()
                else:
                    match()
            
            step_definitions.afterStep()
    
    def _run_outline_steps(self, steps, step_definitions, context):
        self._run_steps(steps, step_definitions, context)

    def __call__(self, features, step_definitions, context):
        with context.run(self.scenario_names, self.tags):
            for filename, feat in features:
                # Skip complete feature if it doesn't have right tags.
                if self.skip_feature_by_tags(feat.tags):
                    context.skip_feature(filename, feat)
                    continue
                
                # Start feature execution.
                with context.feature(filename, feat):
                    for sc in feat.feature_elements:
                        # Skip scenario if it doesn't have right name or tags.
                        if self.skip_scenario_by_name(sc[1].name) or self.skip_scenario_by_tags(sc[1].tags):
                            context.skip_scenario(sc)
                            continue

                        with context.scenario(sc):
                            # Run Before hooks.
                            step_definitions.before()
                            
                            # If feature has Background -- run it.
                            if 'background' in feat:
                                with context.background(feat.background):
                                    self._run_steps(feat.background.steps,  step_definitions, context)
                            
                            # Run scenario or scenario outline.
                            (self._run_steps if sc[0] == 'scenario' \
                                else self._run_outline_steps)(sc[1].steps, step_definitions, context)
                       
                            # Run After hooks.
                            step_definitions.after()
    # end of def __call__(...)
