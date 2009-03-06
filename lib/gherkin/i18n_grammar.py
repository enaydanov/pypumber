#!/usr/bin/env python

import re
from mypeg import *

def background_keyword():
    """ background_keyword <- 'Background', ':' """
    return 'Background', ':'
       
def scenario_keyword():
    """ scenario_keyword <- 'Scenario', ':' """
    return 'Scenario', ':'

def scenario_outline_keyword():
    """ scenario_outline_keyword <- 'Scenario Outline', ':' """
    return 'Scenario Outline', ':'

def step_keyword():
    """ step_keyword <- 'Given' | 'When' | 'Then' | 'And' | 'But' """
    return ['Given', 'When', 'Then', 'And', 'But']

def examples_keyword():
    """ examples_keyword <- 'Examples', ':'? """
    return 'Examples', ZeroOrOne(':')
