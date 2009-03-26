#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

from run import Run

class TestSkipScenario(unittest.TestCase):
    def setUp(self):
        self.r = Run()
    
    def tearDown(self):
        del(self.r)
    
    
        


class TestRun(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()
