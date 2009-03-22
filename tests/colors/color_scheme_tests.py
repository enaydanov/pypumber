#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))
    
from colors import *
from colors.console_colors import DEFAULT_COLORS
from StringIO import StringIO

class TestColorScheme(unittest.TestCase):
    def test_000_empty(self):
        scheme = ColorScheme({}, console_color_string)
        self.assertRaises(AttributeError, getattr, scheme, 'passed')
    
    def test_001_default_write(self):
        scheme = ColorScheme(DEFAULT_COLORS, console_color_string)
        self.assertEqual(scheme.passed(''), '\033[0;32m\033[m')
        
    def test_002_defaut_write_many(self):
        scheme = ColorScheme(DEFAULT_COLORS, console_color_string)
        self.assertEqual(scheme.passed('one'), '\033[0;32mone\033[m')
        self.assertEqual(scheme.passed('two'), '\033[0;32mtwo\033[m')
        self.assertEqual(scheme.failed('three'), '\033[0;31mthree\033[m')
        self.assertEqual(scheme.failed('four'), '\033[0;31mfour\033[m')
        self.assertEqual(scheme.passed('five'), '\033[0;32mfive\033[m')
        self.assertEqual(scheme.failed('six'), '\033[0;31msix\033[m')

    def test_003_write(self):
        out = StringIO()
        scheme = ColorScheme(DEFAULT_COLORS, console_color_string, out)
        scheme.passed('')
        self.assertEqual(out.getvalue(), '\033[0;32m\033[m')
        
    def test_004_write_many(self):
        out = StringIO()
        scheme = ColorScheme(DEFAULT_COLORS, console_color_string, out)
        scheme.passed('one')
        scheme.passed('two')
        scheme.failed('three')
        scheme.failed('four')
        scheme.passed('five')
        scheme.failed('six')
        self.assertEqual(out.getvalue(),
            '\033[0;32mone\033[m'
            '\033[0;32mtwo\033[m'
            '\033[0;31mthree\033[m'
            '\033[0;31mfour\033[m'
            '\033[0;32mfive\033[m'
            '\033[0;31msix\033[m'
        )

if __name__ == '__main__':
    unittest.main()
