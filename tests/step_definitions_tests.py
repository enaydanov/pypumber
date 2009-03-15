#!/usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

from step_definitions import * 
from step_definitions import _get_func_args as get_func_args

class TestGetFuncArgs(unittest.TestCase):
    def test_000_noargs(self):
        def tmp():
            return 1
        self.assertEqual(get_func_args(tmp), ((), None, None, 0))

    def test_001_one_arg(self):
        def tmp(a):
            return a
        self.assertEqual(get_func_args(tmp), (('a',), None, None, 1))

    def test_002_two_args(self):
        def tmp(a, b):
            c = a + b
            return c
        self.assertEqual(get_func_args(tmp), (('a', 'b'), None, None, 2))

    def test_003_only_arg(self):
        def tmp(*arg):
            c = len(arg)
            return c
        self.assertEqual(get_func_args(tmp), ((), 'arg', None, 1))

    def test_004_one_arg_with_arg(self):
        def tmp(a, *arg):
            c = a + len(arg)
            return c
        self.assertEqual(get_func_args(tmp), (('a',), 'arg', None, 2))

    def test_005_two_args_with_arg(self):
        def tmp(a, b, *arg):
            c = a + b + len(arg)
            return c
        self.assertEqual(get_func_args(tmp), (('a', 'b'), 'arg', None, 3))

    def test_006_only_kw(self):
        def tmp(**kw):
            c = len(kw.items())
            return c
        self.assertEqual(get_func_args(tmp), ((), None, 'kw', 1))

    def test_007_one_arg_with_kw(self):
        def tmp(a, **kw):
            c = a + len(kw.items())
            return c
        self.assertEqual(get_func_args(tmp), (('a',), None, 'kw', 2))

    def test_008_two_args_with_kw(self):
        def tmp(a, b, **kw):
            c = a + b + len(kw.items())
            return c
        self.assertEqual(get_func_args(tmp), (('a', 'b'), None, 'kw', 3))

    def test_009_only_arg_and_kw(self):
        def tmp(*arg, **kw):
            c = len(arg) + len(kw.items())
            return c
        self.assertEqual(get_func_args(tmp), ((), 'arg', 'kw', 2))

    def test_010_one_arg_arg_and_kw(self):
        def tmp(a, *arg, **kw):
            c = a + len(arg) + len(kw.items())
            return c
        self.assertEqual(get_func_args(tmp), (('a',), 'arg', 'kw', 3))

    def test_011_two_args_arg_and_kw(self):
        def tmp(a, b, *arg, **kw):
            c = a + b + len(arg) + len(kw.items())
            return c
        self.assertEqual(get_func_args(tmp), (('a', 'b'), 'arg', 'kw', 4))


class TestStepDefinitions(unittest.TestCase):
    def setUp(self):
        self.r = StepDefinitions()
    
    def tearDown(self):
        del(self.r)
    
    def test_000_creation(self):
        self.assert_(hasattr(self.r, 'Given'))
        self.assert_(hasattr(self.r, 'given'))
        self.assert_(hasattr(self.r, 'When'))
        self.assert_(hasattr(self.r, 'when'))
        self.assert_(hasattr(self.r, 'Then'))
        self.assert_(hasattr(self.r, 'then'))
  
    def test_001_given_rule(self):
        @self.r.Given("some rule")
        def tmp():
            return 'tmp'
        self.assertEqual(self.r.given("some rule"), 'tmp')

    def test_002_given_rule_with_named_args(self):
        @self.r.Given(r'(?P<a>\d+) \+ (?P<b>\d+)')
        def sum(a, b):
            return int(a) + int(b)
        self.assertEqual(self.r.given("12 + 15"), 27)

    def test_003_given_rule_with_nonamed_args(self):
        @self.r.Given(r'(\d+) - (\d+)', 'b', 'a')
        def sum(a, b):
            return int(a) - int(b)
        self.assertEqual(self.r.given("10 - 15"), 5)
        
    def test_004_given_rule_with_mixed_args(self):
        @self.r.Given(r'(?P<a>\d+) - (\d+)', 'b')
        def sum(a, b):
            return int(a) - int(b)
        self.assertEqual(self.r.given("10 - 15"), -5)

    def test_005_given_rule_optional_arg(self):
        @self.r.Given(r'some optional( arg)?', 'arg')
        def tmp(arg):
            return arg
        self.assertEqual(self.r.given("some optional arg"), " arg")
        self.assertEqual(self.r.given("some optional"), None)
        
    def test_006_given_rule_more_args(self):
        @self.r.Given(r'(rule)', 'a', 'b', 'c')
        def tmp(a):
            return a
        self.assertRaises(TypeError, self.r.given, "rule")
    
    def test_007_given_rule_less_args(self):
        @self.r.Given(r'(rule)')
        def tmp(a):
            return a
        self.assertEqual(self.r.given("rule"), "rule")

    def test_008_given_rule_list_arg(self):
        @self.r.Given(r'(\d+) \+ (\d+) \+ (\d+)', 'a', 'b', 'c')
        def tmp(*arg):
            return sum([int(a) for a in arg])
        self.assertRaises(TypeError, self.r.given, "1 + 2 + 3")

    def test_009_given_rule_default_args(self):
        @self.r.Given(r'(\d+) \+ (\d+) \+ (\d+)')
        def tmp(a, b, c):
            return int(a) + int(b) + int(c)
        self.assertEqual(self.r.given("1 + 2 + 3"), 6)

    def test_010_given_rule_default_list_args(self):
        @self.r.Given(r'(\d+) \+ (\d+) \+ (\d+)')
        def tmp(*arg):
            return sum([int(a) for a in arg])
        self.assertEqual(self.r.given("1 + 2 + 3"), 6)

    def test_011_given_rule_kw_arg(self):
        @self.r.Given(r'(\d+) \+ (\d+) \+ (\d+)', 'a', 'b', 'c')
        def tmp(**arg):
            return sum([int(a) for a in arg.values()])
        self.assertEqual(self.r.given("1 + 2 + 3"), 6)
    
    def test_008_given_rule_match_not_found(self):
        self.assertRaises(MatchNotFound, self.r.given, "10 - 5")
        
    def test_009_given_rule_redefine(self):
        @self.r.Given(r'(\d+) - (\d+)', 'b', 'a')
        def sum1(a, b):
            return int(a) - int(b)
        
        @self.r.Given(r'(\d+) - (\d+)', 'b', 'a')
        def sum2(a, b):
            return int(a) + int(b)
        
        self.assertEqual(self.r.given("10 - 5"), 15)

    def test_010_given_rule_ambiguous(self):
        @self.r.Given(r'(\d+) - (\d+)', 'b', 'a')
        def sum1(a, b):
            return int(a) - int(b)
        
        @self.r.Given(r'(\d+) - (\d+)?', 'b', 'a')
        def sum2(a, b):
            return int(a) + int(b)
        
        self.assertRaises(AmbiguousString, self.r.given, "10 - 5")

    #~ def test_020_load_from_file(self):
        #~ self.r.load_from_file(os.path.join(os.path.dirname(__file__), 'step_definitions', 'example_import.py'))
        #~ self.assertEqual(self.r.given("some string"), "tmp")

    def test_020_load__file(self):
        self.r.load(os.path.join(os.path.dirname(__file__), 'step_definitions', 'example_import.py'))
        self.assertEqual(self.r.given("some string"), "tmp")

    def test_021_load__dir(self):
        self.r.load(os.path.join(os.path.dirname(__file__), 'step_definitions'))
        self.assertEqual(self.r.given("some string"), "tmp")

    def test_022_load__multiple(self):
        self.r.load(os.path.join(os.path.dirname(__file__), 'step_definitions'))
        self.assertEqual(self.r.given("some string"), "tmp")
        r = StepDefinitions()
        r.load(os.path.join(os.path.dirname(__file__), 'step_definitions'))
        self.assertEqual(r.given("some string"), "tmp")
        self.assertEqual(self.r.given("some string"), "tmp")


if __name__ == '__main__':
    unittest.main()