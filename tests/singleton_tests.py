#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

from singleton import Singleton

class TestSingleton(unittest.TestCase):
    def testSingleton(self):
        class A(Singleton):
            def __init__(self):
                self.a = 0
            
            def inc(self):
                self.a += 1
        
        a = A()
        b = A()
        a.inc()
        b.inc()
        
        self.assertEqual(a, b)
        self.assertEqual(a.a, b.a)
        self.assertEqual(a.a, 2)

if __name__ == '__main__':
    unittest.main()
