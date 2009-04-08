#!/usr/bin/env python

import re
from peg import *

from i18n_grammar import *
from table_grammar import *

# Language definition

def feature(): # done
    """ feature <- white comment white tags white header background? feature_elements comment? """
    return white, comment, white, tags, white, header, ZeroOrOne(background), feature_elements, ZeroOrOne(comment)

def header(): # done
    """ header <- (!(scenario_outline | scenario | background) .)* """
    return ZeroOrMore(Not([scenario_outline, scenario, background]), AnyChar)

def ts(): # done
    """ ts <- (tag (space|eol)+)* """
    return ZeroOrMore(tag, OneOrMore([space, eol]))

def tags(): # done
    """ tags <- white ts """
    return white, ts

@compile_re
def tag_name(): # done
    """ tag_name <- [^@\r\n\t ]+ """
    return Re(r'[^@\r\n\t ]+')
    
def tag(): # done
    """ tag <- '@' tag_name """
    return '@', tag_name

def comment(): # done
    """ comment <- (comment_line white)* """
    return ZeroOrMore(comment_line, white)
    
def comment_line(): # done
    """ comment_line <- '#' line_to_eol """
    return '#', line_to_eol

def background(): # done
    """ background <- comment white background_keyword space* name (eol+ | eof) steps """
    return comment, white, background_keyword, ZeroOrMore(space), name, [OneOrMore(eol), eof], steps
    
def feature_elements(): # done
    """ feature_elements <- (scenario | scenario_outline)* """
    return ZeroOrMore([scenario, scenario_outline])
    
def name(): # done
    """ name <- line_to_eol """
    return line_to_eol

def scenario(): # done
    """ scenario <- comment tags white scenario_keyword space* name white steps white """
    return comment, tags, white, scenario_keyword, ZeroOrMore(space), name, white, steps, white
    
def scenario_outline(): # done
    """ scenario_outline <- comment tags white scenario_outline_keyword space* name white steps examples_sections white """
    return comment, tags, white, scenario_outline_keyword, ZeroOrMore(space), name, white, steps, examples_sections, white

def steps(): # done
    """ steps <- step* """
    return ZeroOrMore(step)

def multi(): # done
    """ multi <- multiline_arg? """
    return ZeroOrOne(multiline_arg)
    
def step(): # done
    """ step <- comment space* step_keyword keyword_space name (eol+ | eof) multi white """
    return comment, ZeroOrMore(space), step_keyword, keyword_space, name, [OneOrMore(eol), eof], multi, white
    
def examples_sections(): # done
    """ examples_sections <- examples* """
    return ZeroOrMore(examples)

def examples(): # done
    """ examples <- space* examples_keyword space* name eol table white """
    return ZeroOrMore(space), examples_keyword, ZeroOrMore(space), name, eol, table, white

def multiline_arg(): # done
    """ multiline_arg <- table | py_string """
    return [table, py_string]
    
def line_to_eol(): # done
    """ line_to_eol <- (!eol .)* """
    return ZeroOrMore(Not(eol), AnyChar)

def s(): # done
    """ s <- (!close_py_string .)* """
    return ZeroOrMore(Not(close_py_string), AnyChar)

# MODIFIED
# was: open_py_string, s, close_py_string
def py_string(): # done
    """ py_string <- open_py_string s close_py_string """
    return indent, open_py_string, s, close_py_string

# NEW
@compile_re
def indent():
    """ indent <- space* """
    return Re(r'[ \t]*')

def quotes(): # done
    """ quotes <- '\"""' """
    return '"""'

# MODIFIED
# was: white, quotes, ZeroOrMore(space), eol
def open_py_string(): # done
    """ open_py_string <- quotes space* eol """
    return  quotes, ZeroOrMore(space), eol

def close_py_string(): # done
    """ close_py_string <- eol space* quotes white """
    return eol, ZeroOrMore(space), quotes, white 

def white(): # done
    """ white <- (space | eol)* """
    return ZeroOrMore([space, eol])
