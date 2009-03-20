#!/usr/bin/env python

from cfg.set_defaults import set_defaults

from pprint import pprint

class Run(object):
    def __init__(self):
        set_defaults(self, 'scenario_names', 'tags', 'strict', 'autoformat', 'backtrace')

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


    def _run_steps(self, steps, step_definitions, reporter):
        current_kw = None
        for step in steps:
            kw = step.step_keyword[0]
            if kw in ['given', 'when', 'then']:
                current_kw = kw
            else:
                if current_kw is None:
                    raise SyntaxError()
            with reporter.step(current_kw, kw, step.step_keyword[1], step.name):
                getattr(step_definitions, current_kw)(step.name)
            
            with reporter.afterStep():
                step_definitions.afterStep()

    def __call__(self, features, step_definitions, reporter):
        with reporter.start(self.scenario_names, self.tags):
            for filename, feat in features:
                # Skip complete feature if it doesn't have right tags.
                if self.skip_feature_by_tags(feat.tags):
                    reporter.skip_feature(filename, feat.header, feat.tags)
                    continue
                
                # Start feature execution.
                with reporter.feature(filename, feat.header, feat.tags):
                    for sc in feat.feature_elements:
                        # Skip scenario if it doesn't have right name or tags.
                        if self.skip_scenario_by_name(sc[1].name) or self.skip_scenario_by_tags(sc[1].tags):
                            reporter.skip_scenario(sc[0], sc[1].scenario_keyword, sc[1].name, sc[1].tags)
                            continue
                        
                        # Run Before hooks.
                        with reporter.before():
                            step_definitions.before()
                        
                        # If feature has Background -- run it.
                        if 'background' in feat:
                            with reporter.background(feat.background.background_keyword):
                                self._run_steps(feat.background.steps,  step_definitions, reporter)
                        
                        # Run scenario.
                        with reporter.scenario(sc[0], sc[1].scenario_keyword, sc[1].name, sc[1].tags):
                            (self._run_steps if sc[0] == 'scenario' \
                                else self._run_outline_steps)(sc[1].steps, step_definitions, reporter)
                       
                        # Run After hooks.
                        with reporter.after():
                            step_definitions.after()
    # end of def __call__(...)
