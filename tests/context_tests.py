#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

from context import Context
from multiplexer import Multiplexer


class Reporter(object):
    def skip_method(self):
        return "skip_method"
    
    def start_method(self, *args):
        self.started_with_args = args
    
    def pass_method(self):
        self.result = "passed"
    
    def fail_method(self, type, value, traceback):
        self.result = "failed: %s: %s" % (type.__name__, value)

    def start_method2(self, *args):
        self.started_with_args2 = args
    
    def pass_method2(self):
        self.result2 = "passed"
    
    def fail_method2(self, type, value, traceback):
        self.result2 = "failed: %s: %s" % (type.__name__, value)
    
    def start_method_with_value(self, *args):
        return args



class TestContext(unittest.TestCase):
    def setUp(self):
        self.r = Reporter()
        self.c = Context(self.r)

    def tearDown(self):
        del(self.r)
        del(self.c)

    def test_000_creation(self):
        pass
    
    def test_001_skip(self):
        self.assertEqual(self.c.skip_method(), "skip_method")
    
    def test_002_method(self):
        self.assertEqual(self.c.method(), self.c)

    def test_003_start_without_args(self):
        with self.c.method():
            pass
        self.assertEqual(self.r.started_with_args, ())

    def test_004_start_with_one_arg(self):
        with self.c.method('arg1'):
            pass
        self.assertEqual(self.r.started_with_args, ('arg1', ))

    def test_005_start_with_two_args(self):
        with self.c.method('arg1', 'arg2'):
            pass
        self.assertEqual(self.r.started_with_args, ('arg1', 'arg2'))

    def test_006_pass(self):
        with self.c.method():
            pass
        self.assertEqual(self.r.result, "passed")
    
    def test_007_fail(self):
        with self.c.method():
            raise Exception("catched exception")
        self.assertEqual(self.r.result, "failed: Exception: catched exception")
        
    def test_008_fail_strict(self):
        self.c.strict = True
        def tmp():
            with self.c.method():
                raise Exception("uncatched exception")
        self.assertRaises(Exception, tmp)
        self.assertEqual(self.r.result, "failed: Exception: uncatched exception")

    def test_009_call_nested_same(self):
        with self.c.method('call1'):
            with self.c.method('call2'):
                pass
        self.assertEqual(self.r.started_with_args, ('call2', ))

    def test_010_pass_nested_same(self):
        with self.c.method('call1'):
            with self.c.method('call2'):
                pass
        self.assertEqual(self.r.result, 'passed')
    
    def test_011_fail_nested_same(self):
        with self.c.method('call1'):
            with self.c.method('call2'):
                raise Exception("catched exception")
        self.assertEqual(self.r.result, 'passed')
    
    def test_012_fail_strict_nested_same(self):
        self.c.strict = True
        def tmp():
            with self.c.method('call1'):
                with self.c.method('call2'):
                    raise Exception("uncatched exception")
        self.assertRaises(Exception, tmp)
        self.assertEqual(self.r.result, 'failed: Exception: uncatched exception')

    def test_013_call_nested(self):
        with self.c.method('call1'):
            with self.c.method2('call2'):
                pass
        self.assertEqual(self.r.started_with_args, ('call1', ))
        self.assertEqual(self.r.started_with_args2, ('call2', ))

    def test_014_pass_nested(self):
        with self.c.method('call1'):
            with self.c.method2('call2'):
                pass
        self.assertEqual(self.r.result, 'passed')
        self.assertEqual(self.r.result2, 'passed')
    
    def test_015_fail_nested(self):
        with self.c.method('call1'):
            with self.c.method2('call2'):
                raise Exception("catched exception")
        self.assertEqual(self.r.result, 'passed')
        self.assertEqual(self.r.result2, 'failed: Exception: catched exception')
    
    def test_016_fail_strict_nested(self):
        self.c.strict = True
        def tmp():
            with self.c.method('call1'):
                with self.c.method2('call2'):
                    raise Exception("uncatched exception")
        self.assertRaises(Exception, tmp)
        self.assertEqual(self.r.result, 'failed: Exception: uncatched exception')
        self.assertEqual(self.r.result2, 'failed: Exception: uncatched exception')
    
    def test_017_pass_undefined(self):
        with self.c.blah():
            pass
    
    def test_018_fail_undefined(self):
        with self.c.blah():
            raise Exception("catched exception")
        
    def test_019_fail_strict_undefined(self):
        self.c.strict = True
        def tmp():
            with self.c.blah():
                raise Exception("uncatched exception")
        self.assertRaises(Exception, tmp)
    
    def test_020_skip_undefined(self):
        self.assertEqual(self.c.skip_blah(), None)
    
    def test_021_return_none(self):
        with self.c.method() as m:
            rv = m
        self.assertEqual(rv, None)
    
    def test_022_return_value(self):
        with self.c.method_with_value('somevalue') as m:
            rv = m
        self.assertEqual(rv, ('somevalue', ))


class TestContextWithMultiplexer(unittest.TestCase):
    def setUp(self):
        self.r1 = Reporter()
        self.r2 = Reporter()
        self.m = Multiplexer(self.r1, self.r2)
        self.c = Context(self.m)
    
    def tearDown(self):
        del(self.c)
        del(self.m)
        del(self.r1)
        del(self.r2)

    def test_000_creation(self):
        pass
    
    def test_001_skip(self):
        self.assertEqual(self.c.skip_method(), ["skip_method", "skip_method"])
    
    def test_002_method(self):
        self.assertEqual(self.c.method(), self.c)

    def test_003_start_without_args(self):
        with self.c.method():
            pass
        self.assertEqual(self.r1.started_with_args, ())
        self.assertEqual(self.r2.started_with_args, ())

    def test_004_start_with_one_arg(self):
        with self.c.method('arg1'):
            pass
        self.assertEqual(self.r1.started_with_args, ('arg1', ))
        self.assertEqual(self.r2.started_with_args, ('arg1', ))

    def test_005_start_with_two_args(self):
        with self.c.method('arg1', 'arg2'):
            pass
        self.assertEqual(self.r1.started_with_args, ('arg1', 'arg2'))
        self.assertEqual(self.r2.started_with_args, ('arg1', 'arg2'))

    def test_006_pass(self):
        with self.c.method():
            pass
        self.assertEqual(self.r1.result, "passed")
        self.assertEqual(self.r2.result, "passed")
    
    def test_007_fail(self):
        with self.c.method():
            raise Exception("catched exception")
        self.assertEqual(self.r1.result, "failed: Exception: catched exception")
        self.assertEqual(self.r2.result, "failed: Exception: catched exception")
        
    def test_008_fail_strict(self):
        self.c.strict = True
        def tmp():
            with self.c.method():
                raise Exception("uncatched exception")
        self.assertRaises(Exception, tmp)
        self.assertEqual(self.r1.result, "failed: Exception: uncatched exception")
        self.assertEqual(self.r2.result, "failed: Exception: uncatched exception")

    def test_009_pass_undefined(self):
        with self.c.blah():
            pass
    
    def test_010_fail_undefined(self):
        with self.c.blah():
            raise Exception("catched exception")
        
    def test_011_fail_strict_undefined(self):
        self.c.strict = True
        def tmp():
            with self.c.blah():
                raise Exception("uncatched exception")
        self.assertRaises(Exception, tmp)

    def test_012_skip_undefined(self):
        self.assertEqual(self.c.skip_blah(), None)

    def test_013_return_none(self):
        with self.c.method() as m:
            rv = m
        self.assertEqual(rv, [None, None])
    
    def test_014_return_value(self):
        with self.c.method_with_value('somevalue') as m:
            rv = m
        self.assertEqual(rv, [('somevalue', ), ('somevalue', )])


if __name__ == '__main__':
    unittest.main()