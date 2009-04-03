#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

import event

from gherkin.feature import *

# Fixture placeholders.

class ListenerPlaceholder(object):
    def __init__(self):
        self.expected_statuses = [[None], ['done']]
        self.feature_started = False
        self.feature_status = None
        
    def __call__(self, type, feature):
        assert type == 'feature'
        assert feature.status in self.expected_statuses[self.feature_started], 'unexpected status: %s' % feature.status
        
        self.feature_started = not self.feature_started
        self.feature_status = feature.status

class ScenarioPlaceholder(object):
    def __init__(self):
        self.invoked = False
    
    def run(self, step_definitions):
        self.invoked = True

# Tests.

class TestFeature(unittest.TestCase):
    def setUp(self):
        self.feature = Feature(feature_elements=[], tags=frozenset())
        self.listener = ListenerPlaceholder()
        event.add_listener(self.listener)
    
    def tearDown(self):
        del(self.feature)
        del(self.listener)
    
    def test_000_default(self):
        self.assertTrue(self.feature.status is None)
    
    def test_001_zero_scenarios(self):
        self.feature.run(None)
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')

    def test_002_one_scenario(self):
        sc = ScenarioPlaceholder()
        self.feature.feature_elements.append(sc)
        self.feature.run(None)
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(sc.invoked)

    def test_003_two_scenarios(self):
        sc1 = ScenarioPlaceholder()
        sc2 = ScenarioPlaceholder()
        self.feature.feature_elements.extend([sc1, sc2])
        self.feature.run(None)
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(sc1.invoked and sc2.invoked)

    def test_004_skip_by_name_invoked(self):
        sc = ScenarioPlaceholder()
        sc.name = 'not skip'
        self.feature.feature_elements.append(sc)
        self.feature.run(None, scenario_names=['not skip'])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(sc.invoked)

    def test_005_skip_by_name_skipped(self):
        sc = ScenarioPlaceholder()
        sc.name = 'skip'
        self.feature.feature_elements.append(sc)
        self.feature.run(None, scenario_names=['not skip'])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(not sc.invoked)

    def test_006_skip_by_name_complex(self):
        sc = [ScenarioPlaceholder() for i in xrange(4)]
        sc[0].name, sc[2].name = ['not skip'] * 2
        sc[1].name, sc[3].name = ['skip'] * 2
        self.feature.feature_elements.extend(sc)
        self.feature.run(None, scenario_names=['not skip'])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(sc[0].invoked and sc[2].invoked and not (sc[1].invoked or sc[3].invoked))

    def test_007_skip_by_line_invoked(self):
        sc = ScenarioPlaceholder()
        sc.lineno = 12
        self.feature.feature_elements.append(sc)
        self.feature.run(None, lines=[12])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(sc.invoked)

    def test_008_skip_by_line_skipped(self):
        sc = ScenarioPlaceholder()
        sc.lineno = 13
        self.feature.feature_elements.append(sc)
        self.feature.run(None, lines=[12])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(not sc.invoked)

    def test_009_skip_by_line_complex(self):
        sc = [ScenarioPlaceholder() for i in xrange(4)]
        sc[0].lineno, sc[1].lineno, sc[2].lineno, sc[3].lineno = range(4)
        self.feature.feature_elements.extend(sc)
        self.feature.run(None, lines=[0, 2])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(sc[0].invoked and sc[2].invoked and not (sc[1].invoked or sc[3].invoked))

    def test_010_skip_by_name_or_line__line(self):
        sc = ScenarioPlaceholder()
        sc.name = 'not skip'
        sc.lineno = 13
        self.feature.feature_elements.append(sc)
        self.feature.run(None, scenario_names=['not skip'], lines=[12])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(not sc.invoked)

    def test_011_skip_by_name_or_line__name(self):
        sc = ScenarioPlaceholder()
        sc.name = 'skip'
        sc.lineno = 12
        self.feature.feature_elements.append(sc)
        self.feature.run(None, scenario_names=['not skip'], lines=[12])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(not sc.invoked)

    def test_012_scenario_without_tag(self):
        sc = ScenarioPlaceholder()
        sc.tags = frozenset()
        self.feature.feature_elements.append(sc)
        self.feature.run(None, tags=['@tag'])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(not sc.invoked)

    def test_013_scenario_positive_tag(self):
        sc = ScenarioPlaceholder()
        sc.tags = frozenset(['@tag'])
        self.feature.feature_elements.append(sc)
        self.feature.run(None, tags=['@tag'])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(sc.invoked)

    def test_014_scenario_negative_tag(self):
        sc = ScenarioPlaceholder()
        sc.tags = frozenset(['@tag'])
        self.feature.feature_elements.append(sc)
        self.feature.run(None, tags=['~@tag'])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(not sc.invoked)
    
    def test_015_scenario_positive_negative_tags(self):
        sc = ScenarioPlaceholder()
        sc.tags = frozenset(['@tag1', '@tag2'])
        self.feature.feature_elements.append(sc)
        self.feature.run(None, tags=['@tag1', '~@tag2'])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(not sc.invoked)
    
    def test_016_scenario_one_positive_tag(self):
        sc = ScenarioPlaceholder()
        sc.tags = frozenset(['@tag1', '@tag3'])
        self.feature.feature_elements.append(sc)
        self.feature.run(None, tags=['@tag1', '@tag2'])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(sc.invoked)
    
    def test_017_feature_positive_tag(self):
        sc1 = ScenarioPlaceholder()
        sc2 = ScenarioPlaceholder()
        sc1.tags = frozenset()
        sc2.tags = frozenset(['@tag'])
        self.feature.feature_elements.extend([sc1, sc2])
        self.feature.tags=frozenset(['@tag'])
        self.feature.run(None, tags=['@tag'])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(sc1.invoked and sc2.invoked)

    def test_018_feature_negative_tag(self):
        sc1 = ScenarioPlaceholder()
        sc2 = ScenarioPlaceholder()
        sc1.tags = frozenset()
        sc2.tags = frozenset(['@tag'])
        self.feature.feature_elements.extend([sc1, sc2])
        self.feature.tags=frozenset(['@tag'])
        self.feature.run(None, tags=['~@tag'])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(not sc1.invoked and not sc2.invoked)

    def test_019_feature_negative_scenario_positive_tags(self):
        sc1 = ScenarioPlaceholder()
        sc2 = ScenarioPlaceholder()
        sc1.tags = frozenset()
        sc2.tags = frozenset(['@tag2'])
        self.feature.feature_elements.extend([sc1, sc2])
        self.feature.tags=frozenset(['@tag1'])
        self.feature.run(None, tags=['~@tag1', '@tag2'])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(not sc1.invoked and not sc2.invoked)

    def test_020_feature_positive_scenario_negative_tags(self):
        sc1 = ScenarioPlaceholder()
        sc2 = ScenarioPlaceholder()
        sc1.tags = frozenset()
        sc2.tags = frozenset(['@tag2'])
        self.feature.feature_elements.extend([sc1, sc2])
        self.feature.tags=frozenset(['@tag1'])
        self.feature.run(None, tags=['@tag1', '~@tag2'])
        
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        self.assertTrue(sc1.invoked and not sc2.invoked)

    def test_021_feature_complex(self):
        sc = [ScenarioPlaceholder() for i in xrange(8)]
        sc[0].tags, sc[2].tags, sc[4].tags, sc[6].tags = [frozenset(['@tag'])] * 4
        sc[1].tags, sc[3].tags, sc[5].tags, sc[7].tags = [frozenset()] * 4
        sc[0].name, sc[1].name, sc[4].name, sc[5].name = ['not skip'] * 4
        sc[2].name, sc[3].name, sc[6].name, sc[7].name = ['skip'] * 4
        for i in xrange(8):
            sc[i].lineno = i
        
        self.feature.feature_elements.extend(sc)
        self.feature.tags=frozenset()
        self.feature.run(None, tags=['@tag'], scenario_names=['not skip'], lines=[0, 1, 2, 3])
        self.assertEqual(self.feature.status, 'done')
        self.assertEqual(self.listener.feature_status, 'done')
        
        self.assertTrue(sc[0].invoked)
        
        for i in xrange(1, 8):
            self.assertFalse(sc[i].invoked)


if __name__ == '__main__':
    unittest.main()
