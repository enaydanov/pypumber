#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

import event

from step_definitions import Undefined, StepSkipped, Pending
from gherkin.step import *

# Fixture placeholders.

class StepDefinitionsAndMatchPlaceholder(object):
    def __init__(self):
        self.skip_steps = False
    
    def __call__(self):
        assert self.string != 'fail', 'failed step'
        
        if self.string == 'skip':
            raise StepSkipped
        
        if self.string == 'under construction':
            raise Pending()

    def given(self, string, multi):
        if string == 'no match':
            raise Undefined()
        self.string = string
        
        return self
    
    when = given
    then = given


class ListenerPlaceholder(object):
    def __init__(self):
        self.expected_statuses = [[None], ['outline', 'skipped', 'undefined', 'pending', 'failed', 'passed']]
        self.step_started = False
        self.step_status = None
        
    def __call__(self, type, step):
        assert type == 'step'
        assert step.status in self.expected_statuses[self.step_started], 'unexpected status: %s' % step.status
        
        self.step_started = not self.step_started
        self.step_status = step.status

# Tests.

class TestStep(unittest.TestCase):
    def setUp(self):
        self.step = Step(multi=None)
        self.listener = ListenerPlaceholder()
        event.add_listener(self.listener)
        self.step_definitions = StepDefinitionsAndMatchPlaceholder()
    
    def tearDown(self):
        del(self.step)
        del(self.listener)
        del(self.step_definitions)
    
    def test_000_default(self):
        self.assertTrue(self.step.status is None)
        self.assertTrue(self.step.match is None)
        self.assertTrue(self.step.exception is None)

    def test_001_outline(self):
        self.step.run(None)
        
        self.assertEqual(self.step.status, 'outline')
        self.assertEqual(self.step.match, None)
        self.assertEqual(self.step.exception, None)
        self.assertEqual(self.listener.step_status, 'outline')
    
    def test_002_given_skipped(self):
        self.step.section = 'given'
        self.step.name = 'skip'
        
        # Pre-condition.
        self.assertEqual(self.step_definitions.skip_steps, False)
        
        self.step.run(self.step_definitions)
        
        self.assertEqual(self.step.status, 'skipped')
        self.assertNotEqual(self.step.match, None)
        self.assertEqual(self.step.exception, None)
        self.assertEqual(self.listener.step_status, 'skipped')
        self.assertEqual(self.step_definitions.skip_steps, False)

    def test_003_given_undefined(self):
        self.step.section = 'given'
        self.step.name = 'no match'
        self.step.run(self.step_definitions)
        
        self.assertEqual(self.step.status, 'undefined')
        self.assertEqual(self.step.match, None)
        self.assertEqual(type(self.step.exception), Undefined)
        self.assertEqual(self.listener.step_status, 'undefined')
        self.assertEqual(self.step_definitions.skip_steps, True)

    def test_004_given_failed(self):
        self.step.section = 'given'
        self.step.name = 'fail'
        self.step.run(self.step_definitions)
        
        self.assertEqual(self.step.status, 'failed')
        self.assertNotEqual(self.step.match, None)
        self.assertEqual(type(self.step.exception), AssertionError)
        self.assertEqual(self.listener.step_status, 'failed')
        self.assertEqual(self.step_definitions.skip_steps, True)

    def test_005_given_pending(self):
        self.step.section = 'given'
        self.step.name = 'under construction'
        self.step.run(self.step_definitions)
        
        self.assertNotEqual(self.step.match, None)
        self.assertEqual(self.step.status, 'pending')
        self.assertEqual(type(self.step.exception), Pending)
        self.assertEqual(self.listener.step_status, 'pending')
        self.assertEqual(self.step_definitions.skip_steps, True)

    def test_006_given_passed(self):
        self.step.section = 'given'
        self.step.name = 'pass'
        self.step.run(self.step_definitions)
        
        self.assertEqual(self.step.status, 'passed')
        self.assertNotEqual(self.step.match, None)
        self.assertEqual(self.step.exception, None)
        self.assertEqual(self.listener.step_status, 'passed')
        self.assertEqual(self.step_definitions.skip_steps, False)


if __name__ == '__main__':
    unittest.main()
