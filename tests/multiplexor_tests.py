#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))


from multiplexor import *


class TestMultiplexor(unittest.TestCase):
    def test_000_multiplexor(self):
        lst = []
        class A(object):
            def __init__(self, v):
                self.v = v
            def method(self, x):
                lst.append(self.v + x)
        a1 = A(1)
        a2 = A(2)
        a3 = A(3)
        a = Multiplexor(a1, a2, a3)
        a.method(2)
        self.assertEqual(lst, [3, 4, 5])
        a.v = 1
        self.assertEqual(a.v, [1, 1, 1])
        del(a.v)
        self.assertFalse(hasattr(a1, 'v'))
        self.assertFalse(hasattr(a2, 'v'))
        self.assertFalse(hasattr(a3, 'v'))
        
    def test_001_defaults(self):
        m = Multiplexor()
        lst1 = []
        lst2 = []
        m.__self__.append(lst1)
        m.__self__.append(lst2)
        m.append(1)
        self.assertEqual(lst1, [1])
        self.assertEqual(lst2, [1])
    
    def test_002_getitems(self):
        m = Multiplexor()
        lst1 = [1, 2, 3]
        lst2 = [3, 4, 5]
        m.__self__.append(lst1)
        m.__self__.append(lst2)
        self.assertEqual(m[1], [2, 4])
        m[1] = 8
        self.assertEqual(lst1, [1, 8, 3])
        self.assertEqual(lst2, [3, 8, 5])
        del(m[1])
        self.assertEqual(lst1, [1, 3])
        self.assertEqual(lst2, [3, 5])

if __name__ == '__main__':
    unittest.main()
