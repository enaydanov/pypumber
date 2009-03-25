#! /usr/bin/env python

import sys, os
from pprint import pprint

def make_path(*path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))

sys.path.insert(0, make_path('lib'))

import backports

from cfg import *
from features import Features

options = Options(
    lang='en',
    multiline=True,
    path=['examples\\complex.feature', ]
)

features = Features()
options(features)

for f, t, l in features:
    pprint(t())
