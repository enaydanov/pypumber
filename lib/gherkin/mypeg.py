#!/usr/bin/env python

"""
Another PEG parser generator for Python.
"""

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"


import types, re


class __Operator(object):
    def __init__(self, *pattern):
        if len(pattern) < 1:
            raise SyntaxError()
        elif len(pattern) == 1:
            self.pattern = pattern[0]
        else:
            self.pattern = pattern

class __Quantifier(__Operator):
    pass

class ZeroOrOne(__Quantifier):
    pass

class ZeroOrMore(__Quantifier):
    pass

class OneOrMore(__Quantifier):
    pass

class __Predicate(__Operator):
    pass

class And(__Predicate):
    pass

class Not(__Predicate):
    pass

AnyChar = re.compile(r'.', re.DOTALL)

class Text:
    def __init__(self, filelike):
        self.text = filelike.read()
        self.cur = 0
        
    def substr(self, length):
        """ Returns substring from current position with length `length' """
        if self.cur + length > len(self.text):
            return self.text[self.cur:]
        else:
            return self.text[self.cur:self.cur+length]
    
    def regexp(self, pattern):
        """ Returns matched string for pattern `pattern' from current position or None if matches not found """
        match = pattern.match(self.text, self.cur)
        if match is not None:
            return match.group()


class PEGParser(object):
    def __init__(self, grammar):
        self.handlers = {
            types.StringType: self.string_terminal,
            type(re.compile('')): self.re_terminal,
            types.FunctionType: self.non_terminal,
            types.TupleType: self.sequence,
            types.ListType: self.alternative,
            type(ZeroOrOne('')): self.zero_or_one,
            type(ZeroOrMore('')): self.zero_or_more,
            type(OneOrMore('')): self.one_or_more,
            type(And('')): self.and_predicate,
            type(Not('')): self.not_predicate,
        }
        self.grammar = grammar


    def string_terminal(self, text, pattern):
        """ Handler for string terminal:
            
            A <- "abc"
        """
        if text.substr(len(pattern)) != pattern:
            raise SyntaxError()
        text.cur += len(pattern)
        
        return pattern 
    
    
    def re_terminal(self, text, pattern):
        """ Handler for regexp terminal:
        
            A <- /re/
            
            Assumes that pattern is compiled regular expression.
        """
        match = text.regexp(pattern)
        if match is None:
            raise SyntaxError()
        text.cur += len(match)
        
        return match
    
    
    def default_rule(self, name, subtree):
        return name, subtree


    def non_terminal(self, text, pattern):
        """ Handler for nonterminal. """
        try:
            result = self.parse(text, pattern())
        except NameError:
            raise SyntaxError()
        if pattern.__name__[0] != '_':
            return getattr(self, pattern.__name__, self.default_rule)(pattern.__name__, result)
        elif pattern.__name__[1] != '_':
            return result
    
    
    def sequence(self, text, pattern):
        """ Handler for sequence:
            
            A <- e1 e2 ... eN
            
            Assumes that sequence represents by tuple.
        """
        result = []
        old_cur = text.cur
        try:
            for i in pattern:
                tmp = self.parse(text, i)
                if tmp is not None:
                    if type(tmp) == types.ListType:
                        result.extend(tmp)
                    else:
                        result.append(tmp)
        except SyntaxError, e:
            text.cur = old_cur
            raise SyntaxError(e)
        
        if len(result) == 1:
            return result[0]
        else:
            return result
    
    
    def alternative(self, text, pattern):
        """ Handler for alternative:
        
            A <- e1 | e2 | ... | eN
            
            Assumes that alternative represents by list.
        """
        for alt in pattern:
            try:
                return self.parse(text, alt)
            except SyntaxError:
                pass
        else:
            raise SyntaxError()
    
    
    def zero_or_one(self, text, pattern):
        """ Handler for zero-or-one quantifier:
        
            A <- e?
        """
        try:
            return self.parse(text, pattern.pattern)
        except SyntaxError:
            pass
    
    
    def zero_or_more(self, text, pattern):
        """ Handler for zero-or-more quantifier:
            
            A <- e*
        """
        result = []
        try:
            while True:
                tmp = self.parse(text, pattern.pattern)
                if tmp is not None:
                    if type(tmp) == types.ListType:
                        result.extend(tmp)
                    else:
                        result.append(tmp)
        except SyntaxError:
            pass
    
        if len(result) == 1:
            return result[0]
        elif len(result):
            return result
    
    
    def one_or_more(self, text, pattern):
        """ Handler for one-or-more quantifier:
            
            A <- e+
        """
        result = []
        tmp = self.parse(text, pattern.pattern)
        if tmp is not None:
            result.append(tmp)
        tmp = self.zero_or_more(text, pattern)
        if type(tmp) == types.ListType:
            result.extend(tmp)
        elif tmp is not None:
            result.append(tmp)
    
        if len(result) == 1:
            return result[0]
        elif len(result):
            return result
        
    
    def not_predicate(self, text, pattern):
        """ Handler for `not' predicate:
        
            A <- !e
        
            If it fails raise SyntaxError exception else return None.
        """
        old_cur = text.cur
        try:
            self.parse(text, pattern.pattern)
        except SyntaxError:
            pass
        else:
            text.cur = old_cur
            raise SyntaxError()
    
    
    def and_predicate(self, text, pattern):
        """ Handler for `and' predicate:
        
            A <- &e
            
            If it fails raise SyntaxError exception else return None.
        """
        old_cur = text.cur
        self.parse(text, pattern.pattern)
        text.cur = old_cur


    def parse(self, text, pattern=None):
        """ Parse text with pattern. If pattern omitted then start with grammar. """
        if pattern is None:
            pattern = self.grammar
        
        return self.handlers[type(pattern)](text, pattern)


if __name__ == '__main__':
    pass