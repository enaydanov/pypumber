#!/usr/bin/env python

"""
Another PEG parser generator for Python.
"""

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"


import types, re, sys

from source import Source, SourceType


class _Operator(object):
    def __init__(self, *pattern):
        if len(pattern) < 1:
            raise SyntaxError()
        elif len(pattern) == 1:
            self.pattern = pattern[0]
        else:
            self.pattern = pattern

class _Quantifier(_Operator):
    pass

class ZeroOrOne(_Quantifier):
    pass

class ZeroOrMore(_Quantifier):
    pass

class OneOrMore(_Quantifier):
    pass

class _Predicate(_Operator):
    pass

class And(_Predicate):
    pass

class Not(_Predicate):
    pass

class Re(object):
    def __init__(self, pattern):
        self.pattern = pattern

def compile_re(fn):
    rv = fn()
    if type(rv) in (types.TupleType, types.ListType):
        compiled_patterns = type(rv)([
            re.compile(r.pattern) if issubclass(r, Re) else r for r in rv
        ])
    elif issubclass(rv, Re):
        compiled_patterns = re.compile(rv.pattern)
    else:
        return fn
    
    def tmp():
        return compiled_patterns
    
    return tmp

AnyChar = re.compile(r'.', re.DOTALL)


class PEGParser(object):
    _shadowed_non_terminals = []
    _skipped_non_terminals = []

    def __init__(self, grammar):
        self._handlers = {
            types.StringType: self._string_terminal,
            type(re.compile('')): self._re_terminal,
            types.FunctionType: self._non_terminal,
            types.TupleType: self._sequence,
            types.ListType: self._alternative,
            type(ZeroOrOne('')): self._zero_or_one,
            type(ZeroOrMore('')): self._zero_or_more,
            type(OneOrMore('')): self._one_or_more,
            type(And('')): self._and_predicate,
            type(Not('')): self._not_predicate,
        }
        self._grammar = grammar
        self._source = None


    def _string_terminal(self, pattern):
        """ Handler for string terminal:
            
            A <- "abc"
        """
        if self._source.substr(len(pattern)) != pattern:
            raise SyntaxError()
        self._source.cur += len(pattern)
        
        return pattern 
    
    
    def _re_terminal(self, pattern):
        """ Handler for regexp terminal:
        
            A <- /re/
            
            Assumes that pattern is compiled regular expression.
        """
        match = self._source.regexp(pattern)
        if match is None:
            raise SyntaxError()
        self._source.cur += len(match)
        
        return match
    
    
    def _default_rule(self, subtree):
        return subtree


    def _non_terminal(self, pattern):
        """ Handler for nonterminal. """
        try:
            result = getattr(self, pattern.__name__, self._default_rule)(self._parse_pattern(pattern()))
        except NameError:
            raise SyntaxError()
        
        if pattern.__name__ in self._shadowed_non_terminals:
            return result
        
        if pattern.__name__ not in self._skipped_non_terminals:
            return pattern.__name__, result
    
    
    def _sequence(self, pattern):
        """ Handler for sequence:
            
            A <- e1 e2 ... eN
            
            Assumes that sequence represents by tuple.
        """
        result = []
        old_cur = self._source.cur
        try:
            for i in pattern:
                tmp = self._parse_pattern(i)
                if tmp is not None:
                    if type(tmp) == types.ListType:
                        result.extend(tmp)
                    else:
                        result.append(tmp)
        except SyntaxError:
            error_at = self._source.cur
            self._source.cur = old_cur
            raise SyntaxError("error at %d.\nPattern: %s" % (error_at, repr(i)))
        
        return result
    
    
    def _alternative(self, pattern):
        """ Handler for alternative:
        
            A <- e1 | e2 | ... | eN
            
            Assumes that alternative represents by list.
        """
        for alt in pattern:
            try:
                return self._parse_pattern(alt)
            except SyntaxError:
                pass
        else:
            raise SyntaxError()
    
    
    def _zero_or_one(self, pattern):
        """ Handler for zero-or-one quantifier:
        
            A <- e?
        """
        try:
            return self._parse_pattern(pattern.pattern)
        except SyntaxError:
            pass
    
    
    def _zero_or_more(self, pattern):
        """ Handler for zero-or-more quantifier:
            
            A <- e*
        """
        result = []
        try:
            while True:
                tmp = self._parse_pattern(pattern.pattern)
                if tmp is not None:
                    if type(tmp) == types.ListType:
                        result.extend(tmp)
                    else:
                        result.append(tmp)
        except SyntaxError:
            pass
    
        if len(result):
            return result
    

    def _one_or_more(self, pattern):
        """ Handler for one-or-more quantifier:
            
            A <- e+
        """
        result = []

        # One..
        tmp = self._parse_pattern(pattern.pattern)
        if type(tmp) == types.ListType:
            result.extend(tmp)
        elif tmp is not None:
            result.append(tmp)

        # ..OrMore
        tmp = self._zero_or_more(pattern)
        if type(tmp) == types.ListType:
            result.extend(tmp)
        elif tmp is not None:
            result.append(tmp)
    
        if len(result):
            return result


    def _not_predicate(self, pattern):
        """ Handler for `not' predicate:
        
            A <- !e
        
            If it fails raise SyntaxError exception else return None.
        """
        old_cur = self._source.cur
        try:
            self._parse_pattern(pattern.pattern)
        except SyntaxError:
            pass
        else:
            self._source.cur = old_cur
            raise SyntaxError()
    
    
    def _and_predicate(self, pattern):
        """ Handler for `and' predicate:
        
            A <- &e
            
            If it fails raise SyntaxError exception else return None.
        """
        old_cur = self._source.cur
        self._parse_pattern(pattern.pattern)
        self._source.cur = old_cur


    def _parse_pattern(self, pattern):
        """ Parse text with pattern. """
        return self._handlers[type(pattern)](pattern)
    
    
    def __call__(self, source, source_type=SourceType.GUESS):
        self._source = Source(source, source_type)
        try:
            return self._parse_pattern(self._grammar)
        finally:
            self._source = None
