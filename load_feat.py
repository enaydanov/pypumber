#! /usr/bin/env python

import sys, os
from pprint import pprint

def make_path(*path):
	return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))

sys.path.append(make_path('lib'))

class Reporter(object):
    class Context(object):
        def __init__(self, in_msg=None, out_msg=None):
            self.in_msg = in_msg
            self.out_msg = out_msg
            
        def __enter__(self):
            if self.in_msg is not None:
                print self.in_msg
        
        def __exit__(self, type, value, traceback):
            if self.out_msg is not None:
                print self.out_msg

    def skip_feature(self, filename, header, tags):
        pass
        
    def skip_scenario(self, kw, i18n_kw, name, tags):
        pass

    def start(self, scenario_names, tags):
        return self.Context()
        
    def feature(self, filename, header, tags):
        return self.Context(in_msg=header)
    
    def before(self):
        return self.Context()
        
    def background(self, kw):
        return self.Context()
        
    def scenario(self, kw, i18n_kw, name, tags):
        return self.Context(in_msg=' '.join([' ', i18n_kw, name, '# tags: ', repr(tags())]))
        
    def step(self, section, kw, i18n_kw, name):
        return self.Context(in_msg=' '.join(['   ', i18n_kw, name]))
    
    def afterStep(self):
        return self.Context()
    
    def after(self):
        return self.Context()


class Rules(object):
    def print_this(self, attr, *args):
        print '>>>', attr, ':', ''.join(args)

    def __getattr__(self, attr):
        return lambda *args: self.print_this(attr, *args)


if __name__ == '__main__':
    from features import Features
    from cfg.options import Options
    from run import Run
    
    features = Features()
    reporter = Reporter()
    step_definitions = Rules()
    r = Run()
    opts = Options(lang='en', path='examples/add.feature', tags=('@sometag', ))
    opts(features, reporter, step_definitions, r)
    
    r(features, step_definitions, reporter)
