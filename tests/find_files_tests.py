#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

from find_files import *

_dir = os.path.join(os.path.dirname(__file__), 'features')

# Shortcuts
dj = lambda *args: os.path.join(_dir, *args)
ap = lambda *args: os.path.abspath(dj(*args))

class TestRun(unittest.TestCase):
    def test_000_single_file(self):
        self.assertEqual(
            find_files(dj('f1.feature')),
            set([ap('f1.feature')])
        )

    def test_001_default_pattern(self):
        self.assertEqual(
            find_files(dj('a2')),
            set([ap('a2', 'c', 'c1.feature'), ap('a2', 'f1')])
        )

    def test_001_default_pattern_relpath(self):
        self.assertEqual(
            find_files(dj('..', 'features', 'a2')),
            set([ap('a2', 'c', 'c1.feature'), ap('a2', 'f1')])
        )


    def test_002_excludes_win(self):
        self.assertEqual(
            find_files(_dir, '[ac]1.feature', ['a\\c']),
            set([ap('a2', 'c', 'c1.feature'), ap('a', 'a1.feature')])
        )

    def test_002_excludes_unix(self):
        self.assertEqual(
            find_files(_dir, '[ac]1.feature', ['a/c']),
            set([ap('a2', 'c', 'c1.feature'), ap('a', 'a1.feature')])
        )

# TODO:
#   test for multiple dirs
#   test for same files


if __name__ == '__main__':
    unittest.main()
