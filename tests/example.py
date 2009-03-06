#!/usr/bin/env python

import os.path, types
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from lib.gherkin.mypeg import Text
from lib.gherkin.feature import FeatureParser
from pprint import pprint

file = open(os.path.join(os.path.dirname(__file__), 'add.feature'))
text = Text(file)
parser = FeatureParser()
pprint(parser.parse(text))
