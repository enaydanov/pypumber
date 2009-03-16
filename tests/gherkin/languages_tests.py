#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

from gherkin.languages import *
from cfg.options import Options
from multiplexer import Multiplexer

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
    
    def test_002_set_language_via_options(self):
        from gherkin.feature_grammar import scenario_keyword
        
        languages = Languages()
        en = Options(lang='en')
        en_lol = Options(lang='en-lol')
        none = Options(lang=None)
        m = Multiplexer(en, none)
        en(languages)
        self.assertEqual(languages.lang, 'en')
        self.assertEqual(scenario_keyword(), (['Scenario'], ':'))
        en_lol(languages)
        self.assertEqual(languages.lang, 'en-lol')
        self.assertEqual(scenario_keyword(), (['MISHUN'], ':'))
        m(languages)
        self.assertEqual(languages.lang, 'en')
        self.assertEqual(scenario_keyword(), (['Scenario'], ':'))
        

if __name__ == '__main__':
    unittest.main()
