#! /usr/bin/env python

import sys, os
from pprint import pprint

def make_path(*path):
	return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))

sys.path.insert(0, make_path('lib'))


class Reporter(object):
    def start_feature(self, filename, header, tags):
        print header
        
    def start_scenario(self, kw, i18n_kw, name, tags):
        print ' ', i18n_kw, name, '# tags: ', repr(tags())
    
    def start_step(self, section, kw, i18n_kw, name):
        print '   ', i18n_kw, name
    
    def pass_step(self):
        print '[passed]'
    

class Rules(object):
    def print_this(self, attr, *args):
        print '>>>', attr, ':', ''.join(args)

    def __getattr__(self, attr):
        return lambda *args: self.print_this(attr, *args)


if __name__ == '__main__':
    from cfg.options import Options

    from features import Features
    from step_definitions import StepDefinitions
    from context import Context
    from run import Run
    
    features = Features()
    step_definitions = StepDefinitions()
    reporter = Reporter()
    context = Context(reporter)
    #step_definitions = Rules()
    run = Run()
    opts = Options(strict=True, lang='en', require='examples', path='examples/add.feature', tags=('@sometag', ))
    opts(features, reporter, step_definitions, run, context)
    
    step_definitions.load()
    
    run(features, step_definitions, context)