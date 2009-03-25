#! /usr/bin/env python

from __future__ import with_statement

import sys, os

def make_path(*path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))

sys.path.insert(0, make_path('lib'))

import backports

from reporters.pretty import PrettyReporter
from colors.console_colors import DEFAULT_COLORS
from colors import ColorScheme, console_color_string
from run import Run
from cfg import *
from multiplexer import Multiplexer
from features import Features
from step_definitions import StepDefinitions

#
# Collect options from different sources:
#   1) default options
#   2) options from profile 'default'
#   3) options from environment
#   4) options from given profile
#   5) command line options
#

cli_opts = CommandLineOptions()

# Use Multiplexer because I want to know the source of all options. 
options = Multiplexer(default_options, ProfileOptions(), EnvOptions(), cli_opts)

# If '--profile' option passed from command line, load such profile. 
if cli_opts.profile:
    options.__outputs__.insert(-1, ProfileOptions(cli_opts.profile))

#
# Configure output:
#   use only 'pretty' format with default color scheme.
#
reporter = PrettyReporter()
reporter.color_scheme = ColorScheme(DEFAULT_COLORS, console_color_string)

#
# Create main app objects.
#
features = Features()
step_definitions = StepDefinitions()
run = Run()

# Apply options.
options(reporter, features,  step_definitions, run)

step_definitions.load()
run(features, step_definitions, reporter)
