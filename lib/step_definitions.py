#!/usr/bin/env python

"""
Step definitions collector.
"""

__author__ = "Eugene Naydanov (e.najdanov@gmail.com)"
__version__ = "$Rev: $"
__date__ = "$Date: $"
__copyright__ = "Copyright (c) 2009 Eugene Naydanov"
__license__ = "Python"


import re, os.path, types, inspect, collections, itertools

from functools import partial
from find_files import find_files
from cfg.set_defaults import set_defaults
from multiplexer import Multiplexer
from split_feature_path import split_feature_path
from objects_space import ObjectsSpace


class MatchNotFound(Exception): 
    """Exception: match not found."""
    pass

class Undefined(MatchNotFound):
    pass

class AmbiguousString(MatchNotFound): 
    """Exception: more than one match found."""
    # TODO: format of lines: keyword, pattern, line
    def __init__(self, string, matches, guess):
        rv = [
            'Ambiguous match of "%s":\n\n' % string, 
            '\n'.join((m[3].re.pattern for m in matches)), 
            '\n\n',
        ]
        if not guess:
            rv.append('You can run again with --guess to make Pypumber be more smart about it\n')
        Exception.__init__(self, ''.join(rv))

class Redundant(Exception):
    """Raised when 2 or more StepDefinition have the same Regexp"""
    def __init__(self, string):
        Exception.__init__(self, 'Multiple step definitions have the same Regexp: "%s"\n' % string)

class StepSkipped(Exception):
    """Exception: step skipped."""
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
        setattr(tmp, '__decorated__', fn)
                
        return tmp

    def _set_sub_decorator(self, name, kw_deco):
        def kw(*args, **kwargs):
            registrator = kw_deco(*args, **kwargs)
            def pending(fn):
                return registrator(self(fn))
            return pending
        setattr(self, name, kw)


class _Value(object):
    def __init__(self, value=None, type='value'):
        self.value = value
        self.type = type

def Value(value=None, type='value'):
    if isinstance(value, _Value):
        return value
    return _Value(value, type)


class Match(object):
    def __init__(self, fn, args, kwargs, matchobj, skip=False):
        self.fn, self.args, self.kwargs, self.matchobj, self.skip = fn, args, kwargs, matchobj, skip
        
        if hasattr(fn, '__decorated__'):
            fn = getattr(fn, '__decorated__')

        self.source_file = inspect.getsourcefile(fn)
        self.source_line = inspect.getsourcelines(fn)[1]
        
        # Extract expected value.
        arg_name = getattr(fn, '__assert_returns__', None)
        if arg_name is not None:
            if arg_name not in self.kwargs:
                raise TypeError("unexpected keyword argument '%s'" % arg_name)
            self.expected_value = self.kwargs.pop(arg_name)

    def __call__(self):
        if self.skip:
            raise StepSkipped
        
        actual_value = self.fn(*self.args, **self.kwargs)
        
        if hasattr(self, 'expected_value'):
            assert self.expected_value == actual_value, 'expected value "%s" not equal to "%s"' % (self.expected_value, actual_value)
        
        return actual_value

def assert_returns(arg):
    def tmp(fn):
        setattr(fn, '__assert_returns__', arg)
        return fn
    return tmp


_STEP_KEYWORDS = ['given', 'when', 'then']
_HOOKS = ['before', 'after', 'afterStep']


class StepDefinitions(object):
    def __init__(self):
        # Options.
        set_defaults(self, 'path', 'excludes', 'require', 'guess', 'verbose', 'dry_run', 'strict')
        
        self.skip_steps = self.dry_run
        
        # Special objects:
        self.__pending = Pending()
        self.__multi = Value(type='multi')
        self.__callback = lambda x: Value(value=x, type='callback')
        self.__world = ObjectsSpace()
        self.__universe = ObjectsSpace()
        
        # Castings.
        self.__castings = {}

        # Create mappings, decorators and runners for step definitions.
        self.__step_definitions = {}
        
        for kw in _STEP_KEYWORDS:
            deco_name = kw.capitalize()
            setattr(self, deco_name, self.__add_rule)
            self.__pending._set_sub_decorator(deco_name, self.__add_rule)
            setattr(self, kw, self.__find_match)
        
        # Create multiplexers and decorators for hooks.
        for hook in _HOOKS:
            setattr(self, hook, Multiplexer())
            setattr(self, hook.capitalize(), partial(self.__add_hook, getattr(self, hook)))
    

    def __add_rule(*args, **step_defaults):
        """Add rule for string to patterns (which is one of the mappings)."""

        # Extract arguments and compile pattern.
        self, string = args[:2]
        patterns = self.__step_definitions
        pattern = re.compile(string)
        args = args[3:]
        
        if [None for p in patterns if p.pattern == string]:
            raise Redundant(string)
        
        # Ensure that there is no name duplication in pattern and args.
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
        
        def registrator(cfunc):
            """Register function as handler for pattern in corresponded map.
            
            Also, bind default func arguments.
            """
            
            # Extract original function.
            if hasattr(cfunc, '__decorated__'):
                func = getattr(cfunc, '__decorated__')
            else:
                func = cfunc
            
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
            
            patterns[pattern] = (cfunc, func_args, func_bindings)

            return cfunc
        
        return registrator

    def __add_hook(self, multiplexer, func):
        """Add hook to multiplexer."""
        multiplexer.__outputs__.append(func)
        
        return func

    def __add_cast(self, **kwargs):
        def registrator(fn):
            self.__castings[fn] = kwargs
            return fn
        return registrator

    #
    # Find match for step.
    # 

    def __find_match(self, string, multi=None):
        """Find match for string in patterns and run handler."""
        match = [ (f[0], f[1], f[2],  m) 
            for f, m in [
                (f, p.search(string)) for p, f in self.__step_definitions.items()
            ] if m
        ]
    
        if len(match) > 1:
            # Try to find best match if option '--guess' passed.
            if self.guess:
                best = sorted(                
                    ((m, len(s), sum(s)) 
                        for m, s in (
                            (m, [len(g) for g in m[3].groups() if g != None]) for m in match
                        )
                    ),
                    cmp=lambda a, b: -1 * cmp(a[1], b[1]) or cmp(a[2], b[2])
                )
                match = [x[0] for x in itertools.takewhile(lambda x: x[1:] == best[0][1:], best)]
                if len(match) > 1:
                    raise AmbiguousString(string, match, self.guess)
            else:
                raise AmbiguousString(string, match, self.guess)
        if not match:
            raise Undefined("match for '%s' not found" % string)

        # Parameters of matched step definition.
        cfunc, func_args, match_bindings, matchobj = match[0]
        
        if self.skip_steps:
            return Match(cfunc, [], match_bindings, matchobj, True)
        
        #
        # Values binding.
        #
        
        if hasattr(cfunc, '__decorated__'):
            func = getattr(cfunc, '__decorated__')
        else:
            func = cfunc

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
            """Return actual (and casted) value of argument."""
            value_handlers = collections.defaultdict(lambda: (lambda x: x.value), {
                'multi': lambda x: multi,
                'value': lambda x: x.value,
                'callback': lambda x: x.value(),
            })
            try:
                value = bindings[attr]
                
                # Get actual value.
                if isinstance(value, _Value):
                    value = value_handlers[value.type](value)
                else:
                    value = matchobj.group(value)
                
                # Cast the value.
                if func in self.__castings and attr in self.__castings[func]:
                    value = self.__castings[func][attr](value)

                return value
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
        if len(unbound_groups) and inspect.getargspec(func)[1]:
            (values.append if len(unbound_groups) == 1 else values.extend)(                    
                matchobj.group(*unbound_groups)
            )
        
        # Sanitize object.
        bindings.default_factory = None
        
        # Substitute values for rest kw arguments.
        for k in bindings:
            bindings[k] = get_value(k)
        
        return Match(cfunc, values, bindings, matchobj)

    #
    # Load all step definitions.
    #

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
        setattr(decorators, 'assert_returns', assert_returns)
        setattr(decorators, 'cast', self.__add_cast)
        setattr(decorators, 'multi', self.__multi)
        setattr(decorators, 'callback', self.__callback)
        setattr(decorators, 'world', self.__world)
        setattr(decorators, 'universe', self.__universe)
        
        
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
        
        # Cleanup world after each scenario
        self.After(self.__world)


if __name__ == '__main__':
    pass
