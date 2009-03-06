#!/usr/bin/env python

import os.path, types

from mypeg import Text
from feature import FeatureParser
from pprint import pprint

file = open(os.path.join(os.path.dirname(__file__), 'add.feature'))
text = Text(file)
parser = FeatureParser()
pprint(parser.parse(text))
