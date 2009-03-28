#! /usr/bin/env python

import sys, os.path, unittest

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

from peg.node import Node

class TestNode(unittest.TestCase):
    def test_000_empty(self):
        n = Node()
        self.assertEqual(n.__dict__, {})

    def test_001_one(self):
        n = Node(arg='value')
        self.assertEqual(n.arg, 'value')
        self.assertEqual(len(n.__dict__), 1)

    def test_002_two(self):
        n = Node(arg1='value1', arg2='value2')
        self.assertEqual(n.arg1, 'value1')
        self.assertEqual(n.arg2, 'value2')
        self.assertEqual(len(n.__dict__), 2)

    def test_003_non_kw(self):
        self.assertRaises(TypeError, Node, 'value')
        
    def test_004_in(self):
        n = Node(arg='value')
        self.assertEqual('arg' in n, True)
        self.assertEqual('xxx' in n, False)

if __name__ == '__main__':
    unittest.main()