#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

from singleton import singleton

class TestSingleton(unittest.TestCase):
    def testSingleton(self):
        @singleton
        class A():
            def __init__(self):
                self.a = 0
            
            def inc(self):
                self.a += 1
        
        a = A()
        a.inc()
        
        b = A()
        b.inc()
        
        self.assertEqual(a, b)
        self.assertEqual(a.a, b.a)
        self.assertEqual(a.a, 2)

if __name__ == '__main__':
    unittest.main()
