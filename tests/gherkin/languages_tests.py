#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

from gherkin.languages import *


class TestLanguages(unittest.TestCase):
    def test_000_creation(self):
        l = Languages()
        self.assertTrue('en' in l)
        self.assertTrue('en' in [x for x in l])
        self.assertEqual(l['en'].given, ['Given'])
        self.assertEqual(l['en']('Scenarios'), 'examples')
        self.assertEqual(l['en'].and_, ['And'])
    
    def test_001_set_language(self):
        from gherkin.feature_grammar import scenario_keyword
        
        self.assertRaises(AttributeError, scenario_keyword)
        set_language('en')
        self.assertEqual(scenario_keyword(), (['Scenario'], ':'))
        set_language('en-lol')
        self.assertEqual(scenario_keyword(), (['MISHUN'], ':'))

if __name__ == '__main__':
    unittest.main()
