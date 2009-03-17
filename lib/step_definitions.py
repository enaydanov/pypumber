#!/usr/bin/env python

"""
Step definitions collector.
"""

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"


import re, os.path, types
from find_files import find_files


class AmbiguousString(Exception): 
    """Exception: more than one match found."""
    pass

class MatchNotFound(Exception): 
    """Exception: match not found."""
    pass

_ARG_FLAG = 0x04
_KW_FLAG = 0x08

def _get_func_args(f):
    arg_name = None
    kw_name = None
    argcount = f.func_code.co_argcount
    varnames = f.func_code.co_varnames
    flags = f.func_code.co_flags
    names = varnames[:argcount]
    
    if flags & _ARG_FLAG:
        arg_name = varnames[argcount]
        argcount += 1
    if flags & _KW_FLAG:
        kw_name = varnames[argcount]
        argcount += 1
    
    return (names, arg_name, kw_name, argcount) 


class StepDefinitions(object):
    def __init__(self):
        self._map_given = {}
        self._map_when = {}
        self._map_then = {}
        self._map_before = {}
        
        # Make decorators and runners for all maps.
        for f in [(f[5:], f) for f in dir(self) if f[:5] == '_map_']:
            setattr(self, f[0].capitalize(),
                lambda string, *args:
                    self.__add_rule(getattr(self, f[1]), string, *args)) 
            setattr(self, f[0],
                lambda string:
                    self.__find_and_run(getattr(self, f[1]), string)) 
    
    
    def __add_rule(self, patterns, string, *args):
        if len(set(args)) != len(args):
            raise TypeError()
        def tmp(func):
            patterns[re.compile(string)] = (func, args)
            return func
        return tmp

    
    def __find_and_run(self, patterns, string):
        """Find match for string in patterns and run handler."""
        match = [ (f[0], f[1], m) 
            for f, m in [
                (f, p.search(string)) for p, f in patterns.items()
            ] if m
        ]
    
        if len(match) > 1:
            raise AmbiguousString
        if not match:
            raise MatchNotFound

        func, args, matchobj, = match[0]
        re_dict = matchobj.groupdict()
        
        func_args = _get_func_args(func)

        # Ensure that *arg not presents in RE and pattern args.
        if func_args[1]:
            if func_args[1] in re_dict.keys():
                raise TypeError()
            if func_args[1] in args:
                raise TypeError()
        
        # Ensure that **kw not presents in RE and pattern args.
        if func_args[2]:
            if func_args[2] in re_dict.keys():
                raise TypeError()
            if func_args[2] in args:
                raise TypeError()
        
        re_set = set(re_dict.keys())
        args_set = set(args)
        
        # Arguments names from RE can't be the same as arguments names passed
        # to pattern.
        if re_set & args_set:
            raise TypeError()
        
        # Extract all unnamed groups from matchobj.
        re_dict_spans = [matchobj.span(k) for k in re_set]
        
        all_spans = {}
        for k in range(1, len(matchobj.groups())+1):
            span = matchobj.span(k)
            if all_spans.has_key(span):
                all_spans[span].append(k)
            else:
                all_spans[span] = [k]
        
        for span in re_dict_spans:
            all_spans[span].pop()
            
        anon_groups = []
        for v in all_spans.values():
            anon_groups.extend(v)
        anon_groups.sort()

        # Build names for unnamed groups.
        #
        # In first place, arguments mentioned in pattern, then arguments from
        # function.
        undefined_args = set(func_args[0]) - re_set - args_set
        names = list(args) + [x for x in func_args[0] if x in undefined_args]

        # If function has defaults, init them first.
        kw_args = {}
        if func.func_defaults is not None:
            defaults = list(func.func_defaults)
            for name in func_args[0][-len(defaults):]:
                kw_args[name] = defaults.pop(0)
                
        # Put anon_groups and names together.
        kw_args.update(re_dict)
        try:
            for name in names:
                kw_args[name] = matchobj.group(anon_groups.pop(0))
        except IndexError:
            raise TypeError()

        # Build values for all non-keyword arguments.        
        values = []
        try:
            for arg in func_args[0]:
                values.append(kw_args.pop(arg))
        except KeyError:
            raise TypeError()
 
        # If there are still some not assigned values put them to values.
        if len(anon_groups):
            values.extend(matchobj.group(*anon_groups))

        return func(*values, **kw_args)


    def load(self, paths, excludes=None):
        import sys, decorators

        for f in [f[5:].capitalize() for f in dir(self) if f[:5] == '_map_']:
            setattr(decorators, f, getattr(self, f))
        
        if type(paths) == types.StringType:
            paths = (paths, )
        
        for file in find_files(paths, '*.py', excludes):
            sys.path.insert(0, os.path.dirname(file))
            try:
                name = os.path.basename(file)[:-3] # get filename and drop .py extension
                if name in sys.modules:
                    reload(sys.modules[name])
                else:
                    __import__(name)
            finally:
                sys.path.pop(0)


if __name__ == '__main__':
    pass
