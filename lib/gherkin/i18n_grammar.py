#!/usr/bin/env python

import re
from peg import *
from table_grammar import space

_language = None

def background_keyword():
    """ background_keyword <- 'Background', ':' """
    return _language.background, ':'
       
def scenario_keyword():
    """ scenario_keyword <- 'Scenario', ':' """
    return _language.scenario, ':'

def scenario_outline_keyword():
    """ scenario_outline_keyword <- 'Scenario Outline', ':' """
    return _language.scenario_outline, ':'

def step_keyword():
    """ step_keyword <- 'Given' | 'When' | 'Then' | 'And' | 'But' """
    return [_language.given, _language.when, _language.then, _language.and_, _language.but]

def examples_keyword():
    """ examples_keyword <- 'Examples', ':'? """
    return _language.examples, ZeroOrOne(':')

def keyword_space():
    if _language.space_after_keyword:
        return OneOrMore(space)
    else:
        return ZeroOrMore(space)
