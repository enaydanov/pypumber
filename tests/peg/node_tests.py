#! /usr/bin/env python

import sys, os.path, unittest

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

from peg.node import Node, _Node as Node_, _NodeMap as NodeMap, _NodeCollection as NodeCollection

class TestNode(unittest.TestCase):
    def test_000_dict(self):
        dict = {'a': 'A', 'b': 'B'}
        n = Node(dict)
        self.assertTrue(isinstance(n, NodeMap))
        self.assertEqual(n(), dict)

    def test_001_list(self):
        list = [0, 1, 2]
        n = Node(list)
        self.assertTrue(isinstance(n, NodeCollection))
        self.assertEqual(n(), list)

    def test_002_tuple(self):
        tuple = (0, 1, 2)
        n = Node(tuple)
        self.assertTrue(isinstance(n, NodeCollection))
        self.assertEqual(n(), tuple)

    def test_003_other(self):
        string = "string"
        n = Node(string)
        self.assertEqual(n, string)


class Test__Node(unittest.TestCase):
    def test_000_creation(self):
        n = Node_("test")
        self.assertEqual(n(), "test")

    def test_001_contains_list(self):
        n = Node_([1, 2])
        self.assertTrue(1 in n)
        self.assertTrue(2 in n)

    def test_002_contains_dict(self):
        n = Node_({1: 2})
        self.assertTrue(1 in n)
        self.assertFalse(2 in n)

    def test_003_getitem_list(self):
        list = [1, 2]
        n = Node_(list)
        self.assertEqual(n[1], 2)
        self.assertRaises(TypeError, lambda: n['1'])
        self.assertRaises(IndexError, lambda: n[100])
        self.assertEqual(n[-2], 1)

    def test_004_getitem_dict(self):
        dict = {1:2, 3:4}
        n = Node_(dict)
        self.assertEqual(n[1], 2)
        self.assertRaises(KeyError, lambda: n['1'])
        self.assertRaises(KeyError, lambda: n[100])
        self.assertRaises(KeyError, lambda: n[-2])


class Test__NodeMap(unittest.TestCase):
    def setUp(self):
        self.dict = {'a': 'A', 'b': 'B'}
        self.n = NodeMap(self.dict)

    def tearDown(self):
        del(self.n)
        del(self.dict)

    def test_000_creation(self):
        self.assertEqual(self.n(), self.dict)

    def test_001_success(self):
        self.assertEqual(self.n.a, 'A')

    def test_002_exception(self):
        self.assertRaises(AttributeError, lambda: self.n.c)

    def test_003_iter(self):
        self.assertEqual([x for x in self.n], self.dict.keys())


class Test__NodeCollection(unittest.TestCase):
    def test_000_creation_list(self):
        list = [1, 2, 3]
        n = NodeCollection(list)
        self.assertEqual(n(), list)

    def test_001_creation_tuple(self):
        tuple = ('a', 'b', 'c')
        n = NodeCollection(tuple)
        self.assertEqual(n(), tuple)

    def test_001_iter_list(self):
        list = [1, 2, 3]
        n = NodeCollection(list)
        self.assertEqual([x for x in n], list)

    def test_003_iter_tuple(self):
        tuple = ('a', 'b', 'c')
        n = NodeCollection(tuple)
        self.assertEqual([x for x in n], list(tuple))

    def test_004_in_tuple(self):
        tuple = ('a', 'b', 'c')
        n = NodeCollection(tuple)
        self.assertTrue('a' in n)
        self.assertFalse('d' in n)

    def test_005_in_list(self):
        list = ['a', 'b', 'c']
        n = NodeCollection(list)
        self.assertTrue('a' in n)
        self.assertFalse('d' in n)
    
    def test_006_equal_empty_tuple(self):
        obj = tuple()
        n = NodeCollection(obj)
        self.assertTrue(n == tuple())

    def test_007_equal_empty_list(self):
        list = []
        n = NodeCollection(list)
        self.assertTrue(n == [])


		
if __name__ == '__main__':
    unittest.main()