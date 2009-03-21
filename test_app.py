#! /usr/bin/env python

import sys, os

def make_path(*path):
	return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))

sys.path.append(make_path('lib'))

from run import Run
from cfg import *
from multiplexer import Multiplexer


cli_opts = CommandLineOptions()

# Use Multiplexer because I want to know the source of all options. 
options = Multiplexer(default_options, ProfileOptions(), EnvOptions(), cli_opts)

# If '--profile' option passed from command line, load such profile. 
if cli_opts.profile:
    options.__outputs__.insert(-1, ProfileOptions(cli_opts.profile))

# Collect reporters from options.
#~ reporters = Options(format=[])
#~ options(reporters)
#~ reporters = Multiplexer(*reporters.reporter)
#~ options(reporters)

run = Run()

# Apply options.
options(run, Languages())


for a in ['path', 'scenario_names', 'excludes', 'tags', 'require', 'autoformat', 'dry_run', 'strict']:
    print "%s:" % a, getattr(run, a)

print Languages().lang
