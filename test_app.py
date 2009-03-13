#! /usr/bin/env python

import sys, os

def make_path(*path):
	return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))

sys.path.append(make_path('lib'))

from cli import CommandLineOptions

cli_opts = CommandLineOptions()

if cli_opts.dry_run:
    print "dry_run"

print cli_opts.snippets
print cli_opts.source
print cli_opts.color
print cli_opts.formatter
print cli_opts.autoformat
