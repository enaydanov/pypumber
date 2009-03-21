#! /usr/bin/env python

import os.path, glob, sys, copy


class Reporter(object):
    # Handlers for reporting about whole run execution.
    #~ def start_run(self, scenario_names, tags):
        #~ pass

    #~ def pass_run(self):
        #~ pass
    
    #~ def fail_run(self, type, value, traceback):
        #~ pass


    # Handlers for reporting of feature execution.
    #~ def skip_feature(self, filename, header, tags):
        #~ pass
        
    #~ def start_feature(filename, header, tags):
        #~ pass

    #~ def pass_feature(self):
        #~ pass
    
    #~ def fail_feature(self, type, value, traceback):
        #~ pass


    # Handlers for reporting of steps execution.
    #~ def start_background(i18n_kw):
        #~ pass

    #~ def pass_background(self):
        #~ pass
    
    #~ def fail_background(self, type, value, traceback):
        #~ pass


    # Handlers for reporting of steps execution.
    #~ def skip_scenario(self, kw, i18n_kw, name, tags):
        #~ pass
    
    #~ def start_scenario(self, kw, i18n_kw, name, tags):
        #~ pass

    #~ def pass_scenario(self):
        #~ pass
    
    #~ def fail_scenario(self, type, value, traceback):
        #~ pass


    # Handlers for reporting of steps execution.
    #~ def start_step(self, section, kw, i18n_kw, name):
        #~ pass
    
    #~ def pass_step(self):
        #~ pass
    
    #~ def fail_step(self, type, value, traceback):
        #~ pass
    
    pass


def load_reporters(d):
    reporters = {}
    sys.path.insert(0, os.path.abspath(d))
    for m in (os.path.basename(file)[:-3] for file in glob.iglob(os.path.join(d, '*.py')) if os.path.isfile(file)):
        try:
            module = __import__(m)
            reporters[m] = (obj for obj in 
                    (getattr(module, name) for name in dir(module)) 
                if isinstance(obj, type) and issubclass(obj, Reporter) and obj != Reporter).next()
        except:
            sys.stderr.write("Warning: unable to load a reporter from %s.py\n" % m)
    sys.path.pop(0)
    
    return reporters
