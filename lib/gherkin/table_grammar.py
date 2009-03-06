#!/usr/bin/env python

import re
from mypeg import *

def table():
    """ table <- table_row+ """
    return OneOrMore(table_row)

def cells():
    """ cells <- (cell '|')+ """
    return OneOrMore(cell, '|')

def table_row():
    """ table_row <- __space* '|' cells __space* (__eol+ | eof) """
    return ZeroOrMore(__space), '|', cells, ZeroOrMore(__space), [OneOrMore(__eol), eof]

def cell():
    """ cell <-  (!('|' | __eol) .)* """
    return ZeroOrMore(Not(['|', __eol]), AnyChar)

def __space():
    """ __space <- [ \t] """
    return re.compile(r'[ \t]')

def __eol():
    """ __eol <- "\n" | ("\r" "\n"?) """
    return ["\n", ("\r", ZeroOrOne("\n"))] 

def eof():
    """ eof <- !. """
    return Not(AnyChar)
