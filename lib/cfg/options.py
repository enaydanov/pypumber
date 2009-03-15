#! /usr/bin/env python

class Options(object):
    def __init__(self, **options):
        self.options = options
    
    def __getattr__(self, attr):
        if attr in self.options:
            return self.options[attr]
        raise AttributeError("A instance has no attribute '%s'" % attr)
    
    def update_run(self, run):
        for opt, value in ((k, v) for k,v in self.options.items() if v is not None):
            if opt in ['tags', 'scenario_names', 'excludes', 'path', 'require']:
                    getattr(run, opt).extend(value)
            elif opt in ['dry_run', 'strict', 'autoformat']:
                setattr(run, opt, value)
