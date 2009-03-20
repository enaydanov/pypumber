#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

from cfg.set_defaults import set_defaults

class A(object):
    pass

class TestSetDefaults(unittest.TestCase):
    def setUp(self):
        self.a = A()
    
    def tearDown(self):
        del(self.a)
        
    def test_000_nothing(self):
        set_defaults(self.a)
        self.assertEqual(dir(self.a), dir(A()))
    
    def test_001_one_accu(self):
        set_defaults(self.a, 'scenario_names')
        self.assertEqual(self.a.scenario_names, [])
        del(self.a.scenario_names)
        self.assertEqual(dir(self.a), dir(A()))
        
    def test_002_one_single(self):
        set_defaults(self.a, 'guess')
        self.assertEqual(self.a.guess, None)
        del(self.a.guess)
        self.assertEqual(dir(self.a), dir(A()))
    
    def test_003_one_other(self):
        self.assertRaises(AttributeError, set_defaults, self.a, 'xxx')
        self.assertEqual(dir(self.a), dir(A()))
    
    def test_004_multiple(self):
        set_defaults(self.a, 'scenario_names', 'guess')
        self.assertEqual(self.a.scenario_names, [])
        self.assertEqual(self.a.guess, None)
        del(self.a.scenario_names)
        del(self.a.guess)
        self.assertEqual(dir(self.a), dir(A()))
    

if __name__ == '__main__':
    unittest.main()
