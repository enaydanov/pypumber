#! /usr/bin/env python

import sys, os.path, shlex

try:
    import yaml
except ImportError:
    sys.stderr.write("Error: unable to import PyYAML module. Please, download it from http://pyyaml.org\n")
    sys.exit()    

from options import Options
from cli_options_parser import parser

_PROFILES = None

if os.path.isfile('pypumber.yml'):
    try:
        f = None
        f = open(_pypumber_yml)
        _PROFILES = yaml.load(f)
    except IOError:
        sys.stderr.write("Error: unable to load `pypumber.yml'\n")
        sys.exit()
    finally:
        if f:
            f.close()

class ProfileOptions(Options):
    def __init__(self, profile='default'):
        Options.__init__(self)
        
        if _PROFILES is not None:
            try:
                opts, args = parser.parse_args(shlex.split(_PROFILES[profile]))
                self.options = opts.__dict__
                self.options['path'] = args
            except KeyError:
                if profile != 'default':
                    sys.stderr.write("Error: there is no profile with name '%s'\n" % profile)
                    sys.exit()
