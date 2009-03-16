#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))


from multiplexer import *


class TestMultiplexer(unittest.TestCase):
    def test_000_multiplexer(self):
        lst = []
        class A(object):
            def __init__(self, v):
                self.v = v
            def method(self, x):
                lst.append(self.v + x)
        a1 = A(1)
        a2 = A(2)
        a3 = A(3)
        a = Multiplexer(a1, a2, a3)
        a.method(2)
        self.assertEqual(lst, [3, 4, 5])
        a.v = 1
        self.assertEqual(a.v, [1, 1, 1])
        del(a.v)
        self.assertFalse(hasattr(a1, 'v'))
        self.assertFalse(hasattr(a2, 'v'))
        self.assertFalse(hasattr(a3, 'v'))
        
    def test_001_defaults(self):
        m = Multiplexer()
        lst1 = []
        lst2 = []
        m.__outputs__.append(lst1)
        m.__outputs__.append(lst2)
        m.append(1)
        self.assertEqual(lst1, [1])
        self.assertEqual(lst2, [1])
    
    def test_002_getitems(self):
        m = Multiplexer()
        lst1 = [1, 2, 3]
        lst2 = [3, 4, 5]
        m.__outputs__.append(lst1)
        m.__outputs__.append(lst2)
        self.assertEqual(m[1], [2, 4])
        m[1] = 8
        self.assertEqual(lst1, [1, 8, 3])
        self.assertEqual(lst2, [3, 8, 5])
        del(m[1])
        self.assertEqual(lst1, [1, 3])
        self.assertEqual(lst2, [3, 5])
    
    def test_003_callable(self):
        a = lambda: 1
        b = lambda: 2
        m = Multiplexer(a, b)
        self.assertEqual(m(), [1, 2])
    
    def test_005_convert_to_list(self):
        m = Multiplexer(1, 2, 3)
        self.assertEqual(list(m), [1, 2, 3])


class TestMultiplexerListOperations(unittest.TestCase):
    def setUp(self):
        self.m = Multiplexer([1, 1], [2, 2], [3, 3])
    
    def tearDown(self):
        del(self.m)

    def test_000_append(self):
        self.m.append(4)
        self.assertEqual(self.m, [[1, 1, 4], [2, 2, 4], [3, 3, 4]])
    
    def test_001_getitem(self):
        self.assertEqual(self.m[-1], [1, 2, 3])
        
    def test_002_setitem(self):
        self.m[-1] = 3
        self.assertEqual(self.m, [[1, 3], [2, 3], [3, 3]])
        
    def test_003_del(self):
        del(self.m[-1])
        self.assertEqual(self.m, [[1], [2], [3]])
        
    def test_004_len(self):
        self.assertEqual(len(self.m), 3)
        
    def test_005_getslice(self):
        self.assertEqual(self.m[1:], [[1], [2], [3]])
        
    def test_006_setslice(self):
        self.m[1:] = ['a']
        self.assertEqual(self.m, [[1, 'a'], [2, 'a'], [3, 'a']])


class Test_Outputs(unittest.TestCase):
    def setUp(self):
        self.m = Multiplexer([1], [2], [3])
    
    def tearDown(self):
        del(self.m)
        
    def test_000_append(self):
        self.m.__outputs__.append([4])
        self.assertEqual(self.m, [[1], [2], [3], [4]])
    
    def test_001_getitem(self):
        self.assertEqual(self.m.__outputs__[-1], [3])
        
    def test_002_setitem(self):
        self.m.__outputs__[-1] = [1, 2, 3]
        self.assertEqual(self.m, [[1], [2], [1, 2, 3]])
        
    def test_003_del(self):
        del(self.m.__outputs__[-1])
        self.assertEqual(self.m, [[1], [2]])
        
    def test_004_len(self):
        self.assertEqual(len(self.m.__outputs__), 3)
        
    def test_005_getslice(self):
        self.assertEqual(self.m.__outputs__[1:], [[2], [3]])
        
    def test_006_setslice(self):
        self.m.__outputs__[1:] = [['a'], ['b']]
        self.assertEqual(self.m, [[1], ['a'], ['b']])
        
    def test_007_iter(self):
        self.assertEqual([x for x in self.m.__outputs__], [[1], [2], [3]])
    
    def test_008_contains(self):
        self.assertTrue([1] in self.m.__outputs__)
        self.assertFalse(1 in self.m.__outputs__)
        self.assertFalse([4] in self.m.__outputs__)



if __name__ == '__main__':
    unittest.main()
