#!/usr/bin/env python

import re
from peg import *

def table():
    """ table <- table_row+ """
    return OneOrMore(table_row)

def cells():
    """ cells <- (cell '|')+ """
    return OneOrMore(cell, '|')

def table_row():
    """ table_row <- space* '|' cells space* (eol+ | eof) """
    return ZeroOrMore(space), '|', cells, ZeroOrMore(space), [OneOrMore(eol), eof]

def cell():
    """ cell <-  (!('|' | eol) .)* """
    return ZeroOrMore(Not(['|', eol]), AnyChar)

def space():
    """ space <- [ \t] """
    return re.compile(r'[ \t]')

def eol():
    """ eol <- "\n" | ("\r" "\n"?) """
    return ["\n", ("\r", ZeroOrOne("\n"))] 

def eof():
    """ eof <- !. """
    return Not(AnyChar)
