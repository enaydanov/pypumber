#! /usr/bin/env python

import sys, os, unittest

def make_path(*path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))

sys.path.append(make_path('lib'))

loader = unittest.TestLoader()
suite = unittest.TestSuite()
for root, dirs, files in os.walk(make_path('tests')):
    sys.path.append(root)
    for module in [__import__(x[:-3]) for x in files if x.endswith('_tests.py')]:
        suite.addTests(loader.loadTestsFromModule(module))
    sys.path.pop()

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite)
