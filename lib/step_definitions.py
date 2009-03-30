#!/usr/bin/env python

"""
Step definitions collector.
"""

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"


import re, os.path, types, inspect, collections
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


class Value(object):
    def __init__(self, value=None, type='value'):
        if isinstance(value, Value):
            self.value = value.value
            self.type = value.type
        else:
            self.value = value
            self.type = type


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
        
        # Special objects:
        self.__pending = Pending()
        self.__multi = Value(type='multi')
        self.__callback = lambda x: Value(value=x, type='callback')

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
            setattr(self, kw, partial(self.__find_match, map))
        
        # Create multiplexers and decorators for hooks.
        for hook in _HOOKS:
            setattr(self, hook, Multiplexer())
            setattr(self, hook.capitalize(), partial(self.__add_hook, getattr(self, hook)))
    
    def __add_rule(*args, **step_defaults):
        """Add rule for string to patterns (which is one of the mappings)."""

        # Compile pattern.
        self, patterns, pattern = args[0], args[1], re.compile(args[2])
        args = args[3:]
        
        # Ensure that there is no any name duplication in pattern and args.
        args_set = set(args)
        if len(args_set) != len(args) or args_set.intersection(pattern.groupindex):
            raise TypeError('duplicate argument names in step definition')

        # Make extended version of pattern.groupindex
        bindings = dict(zip(
            args, 
            sorted(set(
                xrange(1, len(pattern.groupindex) + len(args) + 1)
            ).difference(
                pattern.groupindex.values()
            ))
        ))
        bindings.update(pattern.groupindex)
        
        # Add step defaults to bindings.
        for name, value in step_defaults.items():
            if name in bindings:
                raise TypeError('duplicate argument names in step definition')
            bindings[name] = Value(value)
        
        def registrator(func):
            """Register function as handler for pattern in corresponded map.
            
            Also, bind default func arguments.
            """
            # Get the names and default values of a function's arguments.
            func_args, func_varargs, func_varkw, func_defaults = inspect.getargspec(func)
            
            func_bindings = {}
            
            if func_defaults is not None:
                # Populate func bindings with default function values.
                def assign_default_values(tree, values):
                    for el in tree:
                        value = values.next()
                        if type(el) == types.ListType:
                            assign_default_values(el, iter(value))
                        else:
                            func_bindings[el] = Value(value)
                assign_default_values(func_args[-len(func_defaults):], iter(func_defaults))
            
            # Merge func bindings with step definition bindings.
            func_bindings.update(bindings)
            
            # Show warnings.
            if self.verbose:
                if func_varargs in func_bindings:
                    sys.stderr.write(
                        "%s:%d : "
                        "WARNING! You've used name of positional argument for bindings: '*%s'." 
                        "Did you really want this?\n" \
                        % (inspect.getsourcefile(func), inspect.getsourcelines()[1], func_varargs)
                    )
                if func_varkw in func_bindings:
                    sys.stderr.write(
                        "%s:%d : "
                        "WARNING! You've used name of keyword argument for bindings: '**%s'." 
                        "Did you really want this?\n" \
                        % (inspect.getsourcefile(func), inspect.getsourcelines()[1], func_varargs)
                    )
            
            patterns[pattern] = (func, func_args, func_bindings)

            return func
        
        return registrator

    def __add_hook(self, multiplexer, func):
        """Add hook to multiplexer."""
        multiplexer.__outputs__.append(func)
        
        return func
        
    
    def __find_match(self, patterns, string, multi=None):
        """Find match for string in patterns and run handler."""
        match = [ (f[0], f[1], f[2],  m) 
            for f, m in [
                (f, p.search(string)) for p, f in patterns.items()
            ] if m
        ]
    
        if len(match) > 1:
            # TODO: '--guess'ing
            raise AmbiguousString("there is more than one match for '%s'" % string)
        if not match:
            raise MatchNotFound("match for '%s' not found" % string)

        # Parameters of matched step definition.
        func, func_args, match_bindings, matchobj = match[0]

        # Make list of unbound values.
        unbound_groups = sorted(
            set(
                xrange(1, len(matchobj.groups()) + 1)
            ).difference(
                match_bindings.values()
            )
        )
        
        # Use defaultdict to pop elements from unbound_values if some argument not in match_bindings.
        bindings = collections.defaultdict(lambda: unbound_groups.pop(0), match_bindings)
        
        def get_value(attr):
            value_handlers = collections.defaultdict(lambda: (lambda x: x.value), {
                'multi': lambda x: multi,
                'value': lambda x: x.value,
                'callback': lambda x: x.value(),
            })
            try:
                value = bindings[attr]
                if isinstance(value, Value):
                    return value_handlers[value.type](value)
                return matchobj.group(value)
            except IndexError:
                raise TypeError("%s:%d: unbound variable '%s' for function '%s'" \
                    % (inspect.getsourcefile(func), inspect.getsourcelines(func)[1], attr, func.__name__)
                )

        def make_anon_tuple(tree):
            rv = []
            for el in tree:
                if type(el) == types.ListType:
                    rv.append(make_anon_tuple(el))
                else:
                    rv.append(get_value(el))
                del(bindings[el])

            return rv
        
        # Positional arguments.
        values = []
        
        # Substitute values.
        for arg in func_args:
            if type(arg) == types.ListType:
                values.append(make_anon_tuple(arg))
            else:
                values.append(get_value(arg))
                del(bindings[arg])
        
        # All unused groups pack into positional argument.
        if len(unbound_groups):
            (values.append if len(unbound_groups) == 1 else values.extend)(                    
                matchobj.group(*unbound_groups)
            )
        
        # Sanitize object.
        bindings.default_factory = None
        
        # Substitute values for rest kw arguments.
        for k in bindings:
            bindings[k] = get_value(k)
        
        return Match(func, values, bindings, matchobj)


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
        
        # Set up special objects:
        setattr(decorators, 'pending', self.__pending)
        setattr(decorators, 'multi', self.__multi)
        setattr(decorators, 'callback', self.__callback)
        
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
