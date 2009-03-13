#!/usr/bin/env python

import os
from step_definitions import StepDefinitions
from gherkin.feature import FeatureParser

class Runner(object):
    def __init__(self):
        self.rules = StepDefinitions()
        self.parser = FeatureParser()
        self.kw_map = {
            'Given': self.rules.given,
            'When': self.rules.when,
            'Then': self.rules.then,
        }
        
    def load_step_definitions(self, startdir):
        for root, dirs, files in os.walk(startdir):
            for file in [x for x in files if x.endwith('.py')]:
                self.rules.load_from_file(os.path.join(root, file))

    def run_feature(self, feature_source, source_type=SourceType.GUESS):
        feature = self.parser(feature_source, source_type)
        for sc in feature.feature_elements:
            print sc[0], sc[1].name
            for step in sc[1].steps:
                try:
                    self.kw_map[step.step_keyword](step.name)
                except Exception, e:
                    self.failed(step)
                else:
                    self.passed(step)

    def run_dir(self, startdir):
        for root, dirs, files in os.walk(startdir):
            for file in [x for x in files if x.endswith('.feature')]:
                self.run_feature(os.path.join(root, file), SourceType.FILE)

        
if __name__ == '__main__':
    r = Runner()
    r.load_step_definitions(os.path.join(os.path.dirname(__file__), 'step_definitions'))
    r.run_feature(os.path.join(os.path.dirname(__file__), 'add.feature'))
