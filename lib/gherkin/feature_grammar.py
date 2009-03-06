#!/usr/bin/env python

import re
from mypeg import *

from i18n_grammar import *
from table_grammar import *
from table_grammar import __space, __eol

# Language definition

def feature(): # done
    """ feature <- __white __comment __white tags __white header background? feature_elements __comment? """
    return __white, __comment, __white, tags, __white, header, ZeroOrOne(background), feature_elements, ZeroOrOne(__comment)

def header(): # done
    """ header <- (!(scenario_outline | scenario | background) .)* """
    return ZeroOrMore(Not([scenario_outline, scenario, background]), AnyChar)

def _ts(): # done
    """ _ts <- (tag (__space|__eol)+)* """
    return ZeroOrMore(tag, OneOrMore([__space, __eol]))

def tags(): # done
    """ tags <- __white _ts """
    return __white, _ts

def tag_name(): # done
    """ tag_name <- [^@\n\t ]+ """
    return re.compile(r'[^@\n\t ]+')
    
def tag(): # done
    """ tag <- '@' tag_name """
    return '@', tag_name

def __comment(): # done
    """ __comment <- (comment_line __white)* """
    return ZeroOrMore(comment_line, __white)
    
def comment_line(): # done
    """ comment_line <- '#' _line_to_eol """
    return '#', _line_to_eol

def background(): # done
    """ background <- __comment __white background_keyword __space* (__eol+ | eof) steps """
    return __comment, __white, background_keyword, ZeroOrMore(__space), [OneOrMore(__eol), eof], steps
    
def feature_elements(): # done
    """ feature_elements <- (scenario | scenario_outline)* """
    return ZeroOrMore([scenario, scenario_outline])
    
def name(): # done
    """ name <- _line_to_eol """
    return _line_to_eol

def scenario(): # done
    """ scenario <- __comment tags __white scenario_keyword __space* name (__white | eof) steps __white """
    return __comment, tags, __white, scenario_keyword, ZeroOrMore(__space), name, [__white, eof], steps, __white
    
def scenario_outline(): # done
    """ scenario_outline <- __comment tags __white scenario_outline_keyword __space* name __white steps examples_sections __white """
    return __comment, tags, __white, scenario_outline_keyword, ZeroOrMore(__space), name, __white, steps, examples_sections, __white

def steps(): # done
    """ steps <- step* """
    return ZeroOrMore(step)

def multi(): # done
    """ multi <- multiline_arg? """
    return ZeroOrOne(multiline_arg)
    
def step(): # done
    """ step <- __comment __space* step_keyword __space* name (__eol+ | eof) multi __white """
    return __comment, ZeroOrMore(__space), step_keyword, ZeroOrMore(__space), name, [OneOrMore(__eol), eof], multi, __white
    
def examples_sections(): # done
    """ examples_sections <- examples* """
    return ZeroOrMore(examples)

def examples(): # done
    """ examples <- __space* examples_keyword __space* name? __eol table __white """
    return ZeroOrMore(__space), examples_keyword, ZeroOrMore(__space), ZeroOrOne(name), __eol, table, __white

def multiline_arg(): # done
    """ multiline_arg <- table | py_string """
    return [table, py_string]
    
def _line_to_eol(): # done
    """ _line_to_eol <- (!__eol .)* """
    return ZeroOrMore(Not(__eol), AnyChar)

def s(): # done
    """ s <- (!close_py_string .)* """
    return ZeroOrMore(Not(close_py_string), AnyChar)

def py_string(): # done
    """ py_string <- open_py_string s close_py_string """
    return open_py_string, s, close_py_string

def quotes(): # done
    """ quotes <- '\"""' """
    return '"""'

def open_py_string(): # done
    """ open_py_string <- __white quotes __space* __eol """
    return __white, quotes, ZeroOrMore(__space), __eol

def close_py_string(): # done
    """ close_py_string <- __eol __space* quotes __white """
    return __eol, ZeroOrMore(__space), quotes, __white

def __white(): # done
    """ __white <- (__space | __eol)* """
    return ZeroOrMore([__space, __eol])
