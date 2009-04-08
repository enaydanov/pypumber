#! /usr/bin/env python

import sys, os
from pprint import pprint
from textwrap import fill

def make_path(*path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))

sys.path.insert(0, make_path('lib'))

import backports

from cfg.options import Options
from features import Features

options = Options(
    lang='en',
    multiline=True,
    #path=['examples\\scenario_outline_failing_background.feature', ]
    #path=['examples\\complex.feature', ]
    path=['tmp\\a.feature', ]
    #path=['examples\\self_test\\features\\sample.feature', ]
)

features = Features()
options(features)

for f, t, l in features:
    #pass
    print fill(repr(t))
