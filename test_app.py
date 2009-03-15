#! /usr/bin/env python

import sys, os

def make_path(*path):
	return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))

sys.path.append(make_path('lib'))

from run import Run

from cfg import *

# Prepare run.
run = Run()

default_options.update_run(run)
default_profile = ProfileOptions()
default_profile.update_run(run)
cli_options = CommandLineOptions()
if cli_options.profile:
    profile_options = ProfileOptions(cli_options.profile)
    profile_options.update_run(run)
cli_options.update_run(run)

for a in ['path', 'scenario_names', 'excludes', 'tags', 'require', 'autoformat', 'dry_run', 'strict']:
    print "%s:" % a, getattr(run, a)

#~ print scenario_keyword()

#~ if cli_opts.dry_run:
    #~ print "dry_run"

#~ print cli_opts.snippets
#~ print cli_opts.source
#~ print cli_opts.color
#~ print cli_opts.formatter
#~ print cli_opts.autoformat
#~ print cli_opts.lang

#~ print cli_opts.autoformat