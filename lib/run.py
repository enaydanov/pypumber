#!/usr/bin/env python

import os, glob
from step_definitions import StepDefinitions
from gherkin.feature import FeatureParser
from find_files import find_files


class Run(object):
    def __init__(self):
        for var in ['scenario_names', 'excludes', 'path', 'require']:
            setattr(self, var, [])
        
        for var in ['tags', 'dry_run', 'strict', 'autoformat', 'reporter', 'backtrace']:
            setattr(self, var, None)


    def __call__():
        rules = StepDefinitions()
        parser = FeatureParser()
        reporter = reporter.Multiplexer(self.reporters)

        if self.require:
            rules.load(self.require)
        else:
            rules.load(self.path, self.excludes)
        
        reporter.start(self)
            
        for feature in find_files(self.path, '*.feature', self.excludes):
            process_feature(feature)
            

        reporter.end(self)
