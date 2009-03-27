#! /usr/bin/env python

from cfg.set_defaults import set_defaults
from step_definitions import MatchNotFound, Pending

class Run(object):
    def __init__(self):
        set_defaults(self, 'scenario_names', 'strict', 'dry_run')
        self.__tags = None

    # 'tags' property.
    def get_tags(self):
        return self.__tags
    def set_tags(self, tags):
        if tags is None:
            self.positive_tags, self.negative_tags = set(), set()
        else:
            self.positive_tags = set([tag for tag in tags if tag[0] != '~'])
            self.negative_tags = set([tag[1:] for tag in tags if tag[0] == '~'])
        self.__tags = tags
    tags = property(get_tags, set_tags)


    def skip_feature(self, feature):
        self._run_whole_feature = not (self.tags is None or self.positive_tags)

        tags = set(feature.tags())
        
        if self.tags is None or not tags:
            return False
        
        if self.negative_tags & tags:
            return True
        
        if self.positive_tags & tags:
            self._run_whole_feature = True  # side-effect

        return False


    def skip_scenario(self, sc, lines):
        name, tags, line = sc.name, set(sc.tags()), sc.lineno
        
        # Skip by line number.
        if lines is not None and line not in lines:
            return True
        
        # Skip by scenario name.
        if (self.scenario_names != []) and (name not in self.scenario_names):
            return True

        if self.tags is None:
            return False
        
        # Skip by tags.
        if self.negative_tags & tags:
            return True
        
        if self.positive_tags & tags:
            return False
        
        return not self._run_whole_feature


    def _run_steps(self, sc, step_definitions, reporter):
        current_kw, skip_following_steps = None, self.dry_run
        for step in sc.steps:
            kw = step.kw
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
                
                # Run step definition.
                try:
                    match()
                except Pending, e:  # Pending step.
                    if self.strict:
                        reporter.fail_step(e)
                        skip_following_steps = True
                    else:
                        reporter.pending_step()
                except Exception, e:
                    reporter.fail_step(e)
                    skip_following_steps = True
                else:
                    reporter.pass_step()
            
            # Run AfterStep hooks.
            try:
                step_definitions.afterStep()
            except:
                pass

    def _run_outline_steps(self, *args):
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
                
                # Run Before hooks.
                try:
                    step_definitions.before()
                except:
                    pass
                
                # If feature has background then run it.
                if 'background' in feat:
                    reporter.start_background(feat.background)
                    self._run_steps(feat.background,  step_definitions, reporter)
                    reporter.end_background()

                # Start scenario execution.
                reporter.start_scenario(sc)

                # Run scenario or scenario outline.
                (self._run_steps if sc.kw == 'scenario' \
                    else self._run_outline_steps)(sc, step_definitions, reporter)

                # Scenario finished.
                reporter.end_scenario()

                # Run After hooks.
                try:
                    step_definitions.after()
                except:
                    pass

            # Feature finished.
            reporter.end_feature()
        
        # Run finished.
        reporter.end_run()
