#!/usr/bin/env python

import unittest, sys, os.path
from pprint import pprint

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

from step_definitions import * 
from cfg.options import Options

step_definitions_path = os.path.join(os.path.dirname(__file__), 'step_definitions')


class StepDefaultsFixture(unittest.TestCase):
    def setUp(self):
        self.r = StepDefinitions()
    
    def tearDown(self):
        del(self.r)


class TestStepDefinitions(StepDefaultsFixture):
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
        self.assertEqual(self.r.given("some rule")(), 'tmp')

    def test_002_given_rule_with_named_args(self):
        @self.r.Given(r'(?P<a>\d+) \+ (?P<b>\d+)')
        def sum(a, b):
            return int(a) + int(b)
        self.assertEqual(self.r.given("12 + 15")(), 27)

    def test_003_given_rule_with_nonamed_args(self):
        @self.r.Given(r'(\d+) - (\d+)', 'b', 'a')
        def sum(a, b):
            return int(a) - int(b)
        self.assertEqual(self.r.given("10 - 15")(), 5)
        
    def test_004_given_rule_with_mixed_args(self):
        @self.r.Given(r'(?P<a>\d+) - (\d+)', 'b')
        def sum(a, b):
            return int(a) - int(b)
        self.assertEqual(self.r.given("10 - 15")(), -5)

    def test_005_given_rule_optional_arg(self):
        @self.r.Given(r'some optional( arg)?', 'arg')
        def tmp(arg):
            return arg
        self.assertEqual(self.r.given("some optional arg")(), " arg")
        self.assertEqual(self.r.given("some optional")(), None)
        
    def test_006_given_rule_more_args(self):
        @self.r.Given(r'(rule)', 'a', 'b', 'c')
        def tmp(a):
            return a
        self.assertRaises(TypeError, self.r.given, "rule")
    
    def test_007_given_rule_less_args(self):
        @self.r.Given(r'(rule)')
        def tmp(a):
            return a
        self.assertEqual(self.r.given("rule")(), "rule")

    def test_008_given_rule_list_arg(self):
        @self.r.Given(r'(\d+) \+ (\d+) \+ (\d+)', 'a', 'b', 'c')
        def tmp(*arg):
            return sum([int(a) for a in arg])
        self.assertRaises(TypeError, self.r.given("1 + 2 + 3"))

    def test_009_given_rule_default_args(self):
        @self.r.Given(r'(\d+) \+ (\d+) \+ (\d+)')
        def tmp(a, b, c):
            return int(a) + int(b) + int(c)
        self.assertEqual(self.r.given("10 + 20 + 30")(), 60)

    def test_010_given_rule_default_list_args(self):
        @self.r.Given(r'(\d+) \+ (\d+) \+ (\d+)')
        def tmp(*arg):
            return sum([int(a) for a in arg])
        self.assertEqual(self.r.given("10 + 20 + 30")(), 60)

    def test_011_given_rule_kw_arg(self):
        @self.r.Given(r'(\d+) \+ (\d+) \+ (\d+)', 'a', 'b', 'c')
        def tmp(**arg):
            return sum([int(a) for a in arg.values()])
        self.assertEqual(self.r.given("10 + 20 + 30")(), 60)
    
    def test_012_given_rule_anon_tuples(self):
        @self.r.Given(r'(\d+) \+ (\d+) \+ (\d+)', 'a', 'b', 'c')
        def tmp(a, (b, c)):
            return int(a) + int(b) + int(c)
        self.assertEqual(self.r.given("10 + 20 + 30")(), 60)

    def test_013_given_plus_one_pos_arg(self):
        @self.r.Given(r'(\d+) \+ (\d+)')
        def tmp(a, *args):
            return int(a) + sum([int(d) for d in args])
        self.assertEqual(self.r.given("99 + 1")(), 100)


    def test_014_given_plus_two_pos_arg(self):
        @self.r.Given(r'(\d+) \+ (\d+) \+ (\d+)')
        def tmp(a, *args):
            return int(a) + sum([int(d) for d in args])
        self.assertEqual(self.r.given("99 + 1 + 100")(), 200)
        
    
    def test_015_given_rule_match_not_found(self):
        self.assertRaises(MatchNotFound, self.r.given, "10 - 5")
        
    def test_016_given_rule_redefine(self):
        def tmp():
            @self.r.Given(r'(\d+) - (\d+)', 'b', 'a')
            def sum1(a, b):
                return int(a) - int(b)
            
            @self.r.Given(r'(\d+) - (\d+)', 'b', 'a')
            def sum2(a, b):
                return int(a) + int(b)
        
        self.assertRaises(Redundant, tmp)

    def test_017_given_rule_ambiguous(self):
        @self.r.Given(r'(\d+) - (\d+)', 'b', 'a')
        def sum1(a, b):
            return int(a) - int(b)
        
        @self.r.Given(r'(\d+) - (\d+)?', 'b', 'a')
        def sum2(a, b):
            return int(a) + int(b)
        
        self.assertRaises(AmbiguousString, self.r.given, "10 - 5")

    def test_018_load__file(self):
        self.r.path.append(os.path.join(step_definitions_path, 'example_import.py'))
        self.r.load()
        self.assertEqual(self.r.given("some string")(), "tmp")

    def test_019_load__dir(self):
        self.r.path.append(step_definitions_path)
        self.r.load()
        self.assertEqual(self.r.given("some string")(), "tmp")

    def test_020_load__multiple(self):
        opt = Options(path=step_definitions_path)
        opt(self.r)
        self.r.load()
        self.assertEqual(self.r.given("some string")(), "tmp")
        r = StepDefinitions()
        opt(r)
        r.load()
        self.assertEqual(r.given("some string")(), "tmp")
        self.assertEqual(self.r.given("some string")(), "tmp")


class TestPending(unittest.TestCase):
    def setUp(self):
        self.p = Pending()
    
    def tearDown(self):
        del(self.p)
        
    def test_000_defaults(self):
        self.assertEqual(self.p.pending_message, 'TODO')
    
    def test_001_raising(self):
        try:
            raise self.p
        except Exception, e:
            self.assertEqual(e.args, ('TODO', ))
    
    def test_002_calling(self):
        self.assertRaises(Pending, self.p)
        
    def test_003_catch(self):
        try:
            self.p()
        except Exception, e:
            self.assertEqual(e, self.p)
    
    def test_004_decorating_successful_func(self):
        @self.p
        def tmp():
            pass
        self.assertRaises(Pending, tmp)
    
    def test_005_decorating_pending_func(self):
        @self.p
        def tmp():
            self.p()
        self.assertRaises(Pending, tmp)

    def test_006_decorating_failing_func(self):
        @self.p
        def tmp():
            raise Exception
        self.assertRaises(Pending, tmp)

    def test_007_setattr_func(self):
        def deco(*args, **kwargs):
            def tmp(fn):
                return fn
            return tmp
        
        self.p._set_sub_decorator('deco', deco)
        
        @self.p.deco()
        def succ():
            pass
        
        @self.p.deco()
        def fail():
            raise Exception
        
        self.assertRaises(Pending, succ)
        self.assertRaises(Pending, fail)

    def test_008_setattr_lamda(self):
        deco = lambda *args, **kwargs: (lambda fn: fn)
 
        self.p._set_sub_decorator('deco', deco)
        
        @self.p.deco()
        def succ():
            pass
        
        @self.p.deco()
        def fail():
            raise Exception
        
        self.assertRaises(Pending, succ)
        self.assertRaises(Pending, fail)

    def test_009_setattr_instance_method_of_oldstyle_class(self):
        class A:
            def deco(self, *args, **kwargs):
                def tmp(fn):
                    return fn
                return tmp
        
        a = A()
        self.p._set_sub_decorator('deco', a.deco)
        
        @self.p.deco()
        def succ():
            pass
        
        @self.p.deco()
        def fail():
            raise Exception
        
        self.assertRaises(Pending, succ)
        self.assertRaises(Pending, fail)
    
    def test_010_setattr_instance_method_of_newstyle_class(self):
        class A(object):
            def deco(self, *args, **kwargs):
                def tmp(fn):
                    return fn
                return tmp
        
        a = A()
        self.p._set_sub_decorator('deco', a.deco)
        
        @self.p.deco()
        def succ():
            pass
        
        @self.p.deco()
        def fail():
            raise Exception
        
        self.assertRaises(Pending, succ)
        self.assertRaises(Pending, fail)


class TestStepDefaults(StepDefaultsFixture):
    def test_000_without(self):
        @self.r.Given(r'some rule')
        def _():
            return 'in some rule'
       
        self.assertEqual(self.r.given('some rule')(), 'in some rule')
    
    def test_001_with_one(self):
        @self.r.Given(r'some rule', arg='value')
        def _(arg):
            return 'in some rule with arg == %s' % arg
       
        self.assertEqual(self.r.given('some rule')(), 'in some rule with arg == value')
    
    def test_002_with_wrong_name(self):
        @self.r.Given(r'some rule', xxx='value')
        def _(arg):
            return 'in some rule with arg == %s' % arg
       
        self.assertRaises(TypeError, self.r.given, 'some rule')

    
    def test_003_with_two(self):
        @self.r.Given(r'some rule', arg1='value1', arg2='value2')
        def _(arg1, arg2):
            return 'in some rule with arg1 == %s, arg2 == %s' % (arg1, arg2)
       
        self.assertEqual(self.r.given('some rule')(), 
            'in some rule with arg1 == value1, arg2 == value2')
    
    def test_004_plus_named_group(self):
        @self.r.Given(r'some rule with (?P<group>named group)', arg='value')
        def _(arg, group):
            return 'in some rule with arg == %s, group == %s' % (arg, group)
       
        self.assertEqual(self.r.given('some rule with named group')(), 
            'in some rule with arg == value, group == named group')

    def test_005_plus_named_group_same_name(self):
        def tmp():
            @self.r.Given(r'some rule with (?P<arg>named group)', arg='value')
            def _(arg):
                return 'in some rule with arg == %s' % arg
            
        self.assertRaises(TypeError, tmp)

    def test_006_plus_args(self):
        @self.r.Given(r'some rule with (named group)', 'group', arg='value')
        def _(arg, group):
            return 'in some rule with arg == %s, group == %s' % (arg, group)
       
        self.assertEqual(self.r.given('some rule with named group')(), 
            'in some rule with arg == value, group == named group')

    def test_007_plus_named_group_same_name(self):
        def tmp():
            @self.r.Given(r'some rule with (named group)', 'arg', arg='value')
            def _(arg):
                return 'in some rule with arg == %s' % arg
            
        self.assertRaises(TypeError, tmp)

    def test_008_plus_unnamed_first(self):
        @self.r.Given(r'some rule with (named group)', arg='value')
        def _(group, arg):
            return 'in some rule with arg == %s, group == %s' % (arg, group)
        
        self.assertEqual(self.r.given('some rule with named group')(), 
            'in some rule with arg == value, group == named group')

    def test_009_plus_unnamed_last(self):
        @self.r.Given(r'some rule with (named group)', arg='value')
        def _(arg, group):
            return 'in some rule with arg == %s, group == %s' % (arg, group)
       
        self.assertEqual(self.r.given('some rule with named group')(), 
            'in some rule with arg == value, group == named group')

    def test_010_plus_defaults(self):
        @self.r.Given(r'some rule with named group', arg='value')
        def _(arg, group='named group'):
            return 'in some rule with arg == %s, group == %s' % (arg, group)
        
        self.assertEqual(self.r.given('some rule with named group')(), 
            'in some rule with arg == value, group == named group')

    def test_011_plus_kwargs(self):
        @self.r.Given(r'some rule with arg', arg='value')
        def _(**kwargs):
            return 'in some rule with arg == %s' % kwargs['arg']
        
        self.assertEqual(self.r.given('some rule with arg')(), 'in some rule with arg == value')

if __name__ == '__main__':
    unittest.main()