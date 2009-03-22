#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))
    
from colors.console_colors import *


class TestColor(unittest.TestCase):
    def test_000_empty(self):
        self.assertEqual(color(), ())
    
    def test_001_one(self):
        self.assertEqual(color('blue'), (34,))
    
    def test_002_two(self):
        self.assertEqual(color('blue', 'bold'), (34, 1))
    
    def test_002_undefined(self):
        self.assertRaises(KeyError, color, 'blues')


class TestColorToSeq(unittest.TestCase):
    def test_000_empty(self):
        self.assertEqual(color_to_seq(color()), '\033[m')
    
    def test_001_one(self):
        self.assertEqual(color_to_seq(color('blue')), '\033[34m')
    
    def test_002_two(self):
        self.assertEqual(color_to_seq(color('blue', 'bold')), '\033[34;1m')
    
    def test_003_error(self):
        self.assertRaises(TypeError, color_to_seq, ('blue',))


class TestColorString(unittest.TestCase):
    def test_000_empty(self):
        self.assertEqual(color_string(color(), ''), '\033[m\033[m')
    
    def test_001_non_empty_color(self):
        self.assertEqual(color_string(color('blue'), ''), '\033[34m\033[m')
    
    def test_002_empty_color(self):
        self.assertEqual(color_string(color(), 'str'), '\033[mstr\033[m')
    
    def test_003_non_empty_color(self):
        self.assertEqual(color_string(color('blue'), 'str'), '\033[34mstr\033[m')


if __name__ == '__main__':
    unittest.main()
