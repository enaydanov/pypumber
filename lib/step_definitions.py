#!/usr/bin/env python

"""
Step definitions collector.
"""

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"


import re, os.path, types, inspect
from functools import partial
from find_files import find_files
from cfg.set_defaults import set_defaults
from multiplexer import Multiplexer
from split_feature_path import split_feature_path


class AmbiguousString(Exception): 
    """Exception: more than one match found."""
    pass

class MatchNotFound(Exception): 
    """Exception: match not found."""
    pass

class Pending(Exception):
    """Pending exception and decorator."""
    def __init__(self, message='TODO'):
        super(Pending, self).__init__(message)
        self.pending_message = message
        
    def __call__(self, fn=None):
        if fn is None:
            raise self
        def tmp(*args, **kwargs):
            try:
                fn(*args, **kwargs)
            except:
                raise self
            else:
                raise Pending("Expected pending '%s' to fail. No Error was raised. No longer pending?" % self.pending_message)
        setattr(tmp, 'source_file', inspect.getsourcefile(fn))
        setattr(tmp, 'source_line', inspect.getsourcelines(fn)[1])
        
        return tmp

    def _set_sub_decorator(self, name, kw_deco):
        def kw(*args, **kwargs):
            registrator = kw_deco(*args, **kwargs)
            def pending(fn):
                return registrator(self(fn))
            return pending
        setattr(self, name, kw)

_ARG_FLAG = 0x04
_KW_FLAG = 0x08

def _get_func_args(f):
    # TODO: remove this. Look 'inspect' module.
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
        
        if hasattr(fn, 'source_file'):
            self.source_file = fn.source_file
        else:
            self.source_file = inspect.getsourcefile(fn)
            
        if hasattr(fn, 'source_line'):
            self.source_line = fn.source_line
        else:
            self.source_line = inspect.getsourcelines(fn)[1]

    def __call__(self):
        return self.fn(*self.args, **self.kwargs)


_STEP_KEYWORDS = ['given', 'when', 'then']
_HOOKS = ['before', 'after', 'afterStep']


class StepDefinitions(object):
    def __init__(self):
        # Options.
        set_defaults(self, 'path', 'excludes', 'require', 'guess', 'verbose')
        self.__pending = Pending()

        # Create mappings, decorators and runners for step definitions.
        for kw in _STEP_KEYWORDS:
            # Create map.
            map_name = '_map_%s' % kw
            deco_name = kw.capitalize()
            setattr(self, map_name, {})
            map = getattr(self, map_name)
            
            # Make decorators and runners.
            setattr(self, deco_name, partial(self.__add_rule, map))
            self.__pending._set_sub_decorator(deco_name, getattr(self, deco_name))
            setattr(self, kw, partial(self.__find_and_run, map))
        
        # Create multiplexers and decorators for hooks.
        for hook in _HOOKS:
            setattr(self, hook, Multiplexer())
            setattr(self, hook.capitalize(), partial(self.__add_hook, getattr(self, hook)))
    
    def __add_rule(self, patterns, string, *args):
        """Add rule for string to patterns (which is one of the mappings)."""
        if len(set(args)) != len(args):
            raise TypeError('duplicate argument names in step definition: %s' % args)
        def registrator(func):
            patterns[re.compile(string)] = (func, args)
            return func
        return registrator

    def __add_hook(self, multiplexer):
        """Add hook to multiplexer."""
        def registrator(func):
            multiplexer.__outputs__.append(func)
            return func
        return registrator
    
    def __find_and_run(self, patterns, string, multi=None):
        """Find match for string in patterns and run handler."""
        match = [ (f[0], f[1], m) 
            for f, m in [
                (f, p.search(string)) for p, f in patterns.items()
            ] if m
        ]
    
        if len(match) > 1:
            raise AmbiguousString()
        if not match:
            raise MatchNotFound("match for '%s' not found" % string)

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
            if span in all_spans:
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
                
        # Put named groups.
        kw_args.update(re_dict)
        
        if len(anon_groups):
            anon_groups = matchobj.group(*anon_groups)
        
        # Use 'multi' as first unnamed group.
        if multi is not None:
            anon_groups.insert(0, multi)
        
        # Put anon_groups and names together.
        try:
            for name in names:
                kw_args[name] = anon_groups.pop(0)
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
            values.extend(anon_groups)

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
            paths = [
                (p if os.path.isdir(p) or not os.path.exists(p) else os.path.dirname(p))
                for p, _ in (split_feature_path(p) for p in self.path)
            ]
            excludes = self.excludes

        # Set up decorators.
        for kw in _STEP_KEYWORDS + _HOOKS:
            deco = kw.capitalize()
            setattr(decorators, deco, getattr(self, deco))
        setattr(decorators, 'pending', self.__pending)
        
        assert type(paths) == types.ListType
        
        try:
            saved_stdout = sys.stdout
            sys.stdout = sys.stderr
            
            for file in find_files(paths, '*.py', excludes):
                sys.path.insert(0, os.path.dirname(file))
                try:
                    name = os.path.basename(file)[:-3] # get filename and drop .py extension
                    
                    if name in sys.modules:
                        reload(sys.modules[name])
                    else:
                        __import__(name)
                except:
                    sys.stderr.write("Warning: an exception was raised during importing '%s' file" % file)
                    if self.verbose:
                        import traceback
                        sys.stderr.write(':\n')
                        traceback.print_exc()
                    else:
                        sys.stderr.write('. Use --verbose for more details.\n')
                finally:
                    sys.path.pop(0)
        finally:
            sys.stdout = saved_stdout


if __name__ == '__main__':
    pass
