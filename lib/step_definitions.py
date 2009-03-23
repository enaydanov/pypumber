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
from cfg.set_defaults import set_defaults
from multiplexer import Multiplexer


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


class Match(object):
    def __init__(self, fn, args, kwargs, matchobj):
        self.fn, self.args, self.kwargs, self.matchobj = fn, args, kwargs, matchobj
    
    def __call__(self):
        return self.fn(*self.args, **self.kwargs)

_DUMMY_MATCH = Match(lambda: None, [], {}, None)


_STEP_KEYWORDS = ['given', 'when', 'then']
_HOOKS = ['before', 'after', 'afterStep']

class DryRun(object):
    def __init__(self):
        for kw in _STEP_KEYWORDS:
            setattr(self, kw, lambda *args: _DUMMY_MATCH)
        
        for hook in _HOOKS:
            setattr(self, hook, lambda: None)

    def load():
        pass


class StepDefinitions(object):
    def __init__(self):
        # Options.
        set_defaults(self, 'path', 'excludes', 'require', 'guess')
        
        def first_arg_closure(first_arg, fn):
            def tmp(*args):
                return fn(first_arg, *args)
            return tmp
        
        # Create mappings, decorators and runners for step definitions.
        for kw in _STEP_KEYWORDS:
            # Create map.
            map_name = '_map_%s' % kw
            setattr(self, map_name, {})
            map = getattr(self, map_name)
            
            # Make decorators and runners.
            setattr(self, kw.capitalize(), first_arg_closure(map, self.__add_rule)) 
            setattr(self, kw, first_arg_closure(map, self.__find_and_run))
        
        # Create multiplexers and decorators for hooks.
        for hook in _HOOKS:
            setattr(self, hook, Multiplexer())
            setattr(self, hook.capitalize(), first_arg_closure(getattr(self, hook), self.__add_hook))
    
    
    def __add_rule(self, patterns, string, *args):
        """Add rule for string to patterns (which is one of the mappings)."""
        if len(set(args)) != len(args):
            raise TypeError()
        def tmp(func):
            patterns[re.compile(string)] = (func, args)
            return func
        return tmp

    def __add_hook(self, multiplexer):
        """Add hook to multiplexer."""
        def tmp(func):
            multiplexer.__outputs__.append(func)
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

        return Match(func, values, kw_args, matchobj)


    def load(self):
        """Load step definitions from configured paths."""
        import sys, decorators

        # TODO: load first from 'support' dir.
        
        # Set up paths. 
        if self.require:
            paths = self.require
            excludes = None
        else:
            paths = [(p if os.path.isdir(p) or not os.path.exists(p) else os.path.dirname(p)) for p in self.path]
            excludes = self.excludes

        # Set up decorators.
        for kw in _STEP_KEYWORDS + _HOOKS:
            deco = kw.capitalize()
            setattr(decorators, deco, getattr(self, deco))
        
        assert type(paths) == types.ListType
        
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
