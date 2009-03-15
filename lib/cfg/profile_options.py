#! /usr/bin/env python

import sys, os.path, shlex

try:
    import yaml
except ImportError:
    sys.stderr.write("Error: unable to import PyYAML module. Please, download it from http://pyyaml.org\n")
    sys.exit()    

from options import Options
from cli_options_parser import parser

_pypumber_yml = os.path.join(os.path.dirname(__file__), '..',  '..', 'pypumber.yml')

try:
    f = None
    f = open(_pypumber_yml)
    _profiles = yaml.load(f)
except IOError:
    sys.stderr.write("Error: unable to load `pypumber.yml'\n")
    sys.exit()
finally:
    if f:
        f.close()

class ProfileOptions(Options):
    def __init__(self, profile='default'):
        Options.__init__(self)
        
        opts, args = parser.parse_args(shlex.split(_profiles[profile]))
        self.options = opts.__dict__
        self.options['path'] = args
