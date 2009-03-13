#! /usr/bin/env python

import unittest, sys, os.path, copy

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))


from reporter import *


class TestLoadReporters(unittest.TestCase):
    def test_000_register(self):
        dir = os.path.join(os.path.dirname(__file__), 'reporters')
        old_sys_path = copy.copy(sys.path)
        reporters = load_reporters(dir)
        self.assertEqual(old_sys_path, sys.path)
        self.assertEqual(len(reporters), 1)
        self.assertTrue('dumb' in reporters)
        self.assertTrue(issubclass(reporters['dumb'], Reporter))
        self.assertEqual(reporters['dumb'].__name__, 'DumbReporter')


if __name__ == '__main__':
    unittest.main()
