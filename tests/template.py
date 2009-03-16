#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

class Test(unittest.TestCase):
    def test_000_default(self):
        pass

if __name__ == '__main__':
    unittest.main()
