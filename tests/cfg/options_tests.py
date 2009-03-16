#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))


from cfg.options import Options
from multiplexer import Multiplexer 


class Test(unittest.TestCase):
    def setUp(self):
        self.opts = Options(opt1='opt1', opt2='opt2', opt3=['alt1', 'alt2'])


    def tearDown(self):
        del(self.opts)


    def test_000_access(self):
        self.assertEqual(self.opts.opt1, 'opt1')
        self.assertEqual(self.opts.opt2, 'opt2')
        self.assertEqual(self.opts.opt3, ['alt1', 'alt2'])


    def test_001_apply_none(self):
        class A:
            def __init__(self):
                self.opt1 = None
                self.opt3 = None

        a = A()
        self.opts(a)

        self.assertEqual(a.opt1, 'opt1')
        self.assertRaises(AttributeError, lambda: a.opt2)
        self.assertEqual(a.opt3, ['alt1', 'alt2'])


    def test_002_apply_not_list(self):
        class A:
            def __init__(self):
                self.opt1 = 'opt0'
                self.opt3 = 'opt0'

        a = A()
        self.opts(a)

        self.assertEqual(a.opt1, 'opt1')
        self.assertRaises(AttributeError, lambda: a.opt2)
        self.assertEqual(a.opt3, ['alt1', 'alt2'])


    def test_003_apply_list(self):
        class A:
            def __init__(self):
                self.opt1 = ['alt0']
                self.opt3 = ['alt0']

        a = A()
        self.opts(a)

        self.assertEqual(a.opt1, ['alt0', 'opt1'])
        self.assertRaises(AttributeError, lambda: a.opt2)
        self.assertEqual(a.opt3, ['alt0', 'alt1', 'alt2'])


    def test_004_apply_multiple(self):
        class A:
            def __init__(self):
                self.opt1 = None
                self.opt3 = []

        class B:
            def __init__(self):
                self.opt2 = []
                self.opt3 = ['alt0']
        
        a = A()
        b = B()
        
        self.opts(a, b)
        
        self.assertEqual(a.opt1, 'opt1')
        self.assertRaises(AttributeError, lambda: a.opt2)
        self.assertEqual(a.opt3, ['alt1', 'alt2'])
        self.assertRaises(AttributeError, lambda: b.opt1)
        self.assertEqual(b.opt2, ['opt2'])
        self.assertEqual(b.opt3, ['alt0', 'alt1', 'alt2'])


    def test_005_multiplexer_apply(self):
        class A:
            def __init__(self):
                self.opt1 = None
                self.opt2 = []
                self.opt3 = []
                self.opt4 = 'default'
                self.opt5 = 'default'
                self.opt6 = 'default'
        
        self.opts.options['opt6'] = 'opt6'
        self.opts.options['opt7'] = 'opt7'
        opts2 = Options(opt1='foo', opt2='bar', opt3=['baz'], opt4='opt4', opt7='opt7')
        
        a = A()
        m = Multiplexer(opts2, self.opts)
        m(a)

        self.assertEqual(a.opt1, 'opt1')
        self.assertEqual(a.opt2, ['bar', 'opt2'])
        self.assertEqual(a.opt3, ['baz', 'alt1', 'alt2'])
        self.assertEqual(a.opt4, 'opt4')
        self.assertEqual(a.opt5, 'default')
        self.assertEqual(a.opt6, 'opt6')
        self.assertRaises(AttributeError, lambda: a.opt7)
        

if __name__ == '__main__':
    unittest.main()
