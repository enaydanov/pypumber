#!/usr/bin/env python

import rules
import os
from gherkin.mypeg import Text
from gherkin.feature import FeatureParser

class Runner(object):
    def __init__(self):
        self.rules = rules.Rules()
        self.parser = FeatureParser()
        self.kw_map = {
            'Given': self.rules.given,
            'When': self.rules.when,
            'Then': self.rules.then,
        }
        
    def load_step_definitions(self, startdir):
        for root, dirs, files in os.walk(startdir):
            for file in files:
                if file[-3:] == '.py':
                    self.rules.load_from_file(os.path.join(root, file))

    def run_feature(self, feature_file):
        feature = self.parser.parse(Text(open(feature_file)))
        for sc in feature['feature_elements']:
            print sc[0], sc[1]['name']
            for step in sc[1]['steps']:
                try:
                    self.kw_map[step['step_keyword']](step['name'])
                except Exception, e:
                    print "[FAILED]", step['step_keyword'], step['name']
                else:
                    print "[PASSED]", step['step_keyword'], step['name']
        
if __name__ == '__main__':
    r = Runner()
    r.load_step_definitions(os.path.join(os.path.dirname(__file__), 'step_definitions'))
    r.run_feature(os.path.join(os.path.dirname(__file__), 'add.feature'))
