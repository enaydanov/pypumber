#! /usr/bin/env python

import os.path, glob, sys, copy


class Reporter(object):
    def __call__(self, msg_type, msg_value):
        getattr(self, msg_type, lambda x: None)(msg_value)


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
