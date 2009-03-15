#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

from attribute_mapper import AttributeMapper

class TestAttributeMapper(unittest.TestCase):
    def test_000_creation(self):
        d = {'a': ['A', 'B'], 'b': ['C']}
        l = AttributeMapper(d, lambda a, b: a in b)
        self.assertEqual(l.b, d['b'])
        self.assertRaises(AttributeError, lambda: l.c)
        self.assertEqual(l['b'], d['b'])
        self.assertEqual(l('A'), 'a')
        self.assertEqual(l('B'), 'a')
        self.assertEqual(l('C'), 'b')
        self.assertEqual(l('D'), None)
        self.assertEqual([x for x in l], d.keys())
    
    def test_001_keywords(self):
        d = {'and': 'And', 'and_': 'And_'}
        l = AttributeMapper(d)
        self.assertEqual(l.and_, 'And')
        self.assertEqual(l.and__, 'And_')
        self.assertEqual(l('And'), 'and')
        self.assertEqual(l('And_'), 'and_')
        

if __name__ == '__main__':
    unittest.main()
