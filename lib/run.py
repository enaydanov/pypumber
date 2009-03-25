#! /usr/bin/env python

from cfg.set_defaults import set_defaults
from step_definitions import MatchNotFound

class ButFailed(Exception):
    pass

class Run(object):
    def __init__(self):
        set_defaults(self, 'scenario_names', 'tags', 'strict', 'dry_run')


    def skip_feature(self, feature):
        self._run_whole_feature = False
        
        tags = feature.tags
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


    def skip_scenario(self, scenario, lines):
        name, tags, line = scenario[1].name, scenario[1].tags, scenario[1].scenario_keyword[1]
        
        # Skip by line number.
        if lines is not None and line not in lines:
            return True
        
        # Skip by scenario name.
        if (self.scenario_names != []) and (name not in self.scenario_names):
            return True

        if self.tags is None:
            return False
        
        # Skip by tags.
        skip = not self._run_whole_feature
        for tag in self.tags:
            if tag[0] == '~':
                if tag[1:] in tags:
                    return True
            else:
                if tag in tags:
                    skip = False
        return skip


    def _run_steps(self, steps, step_definitions, reporter):
        current_kw, skip_following_steps = None, self.dry_run
        for step in steps:
            kw = step.step_keyword[0]
            if kw in ['given', 'when', 'then']:
                current_kw = kw
            else:
                # Raise SyntaxError if steps not start with Given, When or Then
                if current_kw is None:
                    raise SyntaxError()
            
            # Begin step execution.
            reporter.start_step(current_kw, step)
            
            # Try to find step definition.
            try:
                match = getattr(step_definitions, current_kw)(step.name, step.multi)
                reporter.step_definition(match)
            except MatchNotFound:
                reporter.undefined_step()
                
                # Skip execution of following steps if '--strict' option passed.
                if self.strict:
                    skip_following_steps = True
            else:
                # Skip execution of step in two cases:
                #   1) Previously, there is some failed step, or
                #   2) Some undefined step and option '--strict' passed.
                if skip_following_steps:
                    reporter.skip_step()
                    continue
                
                but = (kw == 'but')
                
                # Run step definition.
                try:
                    match()
                    
                    # If all fine, but we are running But step then raise ButFailed exception.
                    if but:
                        raise ButFailed(step.name)
                except Exception, e:
                    if but and not issubclass(e, ButFailed):  # But step passed.
                        reporter.pass_step()
                    else:
                        reporter.fail_step(e)
                        skip_following_steps = True
                else:
                    reporter.pass_step()
            
            # Run AfterStep hooks.
            try:
                step_definitions.afterStep()
            except:
                pass

    def _run_outline_steps(*args):
        self._run_steps(*args)

    def __call__(self, features, step_definitions, reporter):
        reporter.start_run(self.scenario_names, self.tags)
        for filename, feat, lines in features:
            # Skip complete feature if it doesn't match tags.
            if self.skip_feature(feat):
                reporter.skip_feature(filename, feat)
                continue
            
            # Start feature execution.
            reporter.start_feature(filename, feat)
            for sc in feat.feature_elements:

                # Skip scenario if it doesn't match names, lines or tags.
                if self.skip_scenario(sc, lines):
                    reporter.skip_scenario(sc)
                    continue
                
                # Start scenario execution.
                reporter.start_scenario(sc)
                
                # Run Before hooks.
                try:
                    step_definitions.before()
                except:
                    pass
                
                # If feature has background then run it.
                if 'background' in feat:
                    reporter.start_background()
                    self._run_steps(feat.background.steps,  step_definitions, reporter)
                    reporter.end_background()

                # Run scenario or scenario outline.
                (self._run_steps if sc[0] == 'scenario' \
                    else self._run_outline_steps)(sc[1].steps, step_definitions, reporter)
           
                # Run After hooks.
                try:
                    step_definitions.after()
                except:
                    pass
                
                # Scenario finished.
                reporter.end_scenario()
            
            # Feature finished.
            reporter.end_feature()
        
        # Run finished.
        reporter.end_run()
