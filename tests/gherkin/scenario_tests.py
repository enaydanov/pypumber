#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

import event

from gherkin.scenario import *

# Fixture placeholders.

class StepDefinitionsPlaceholder(object):
    def __init__(self):
        self.skip_steps = False
        self.dry_run = False
        self.before_called = 0
        self.after_called = 0
    
    def before(self):
        self.before_called += 1
    
    def after(self):
        self.after_called += 1

class ListenerPlaceholder(object):
    def __init__(self):
        self.expected_statuses = [[None], ['passed', 'failed']]
        self.scenario_started = False
        self.scenario_status = None
        
    def __call__(self, type, scenario):
        assert type == 'scenario'
        assert scenario.status in self.expected_statuses[self.scenario_started], 'unexpected status: %s' % scenario.status
        
        self.scenario_started = not self.scenario_started
        self.scenario_status = scenario.status

class StepPlaceholder(object):
    def __init__(self, fail_message=None):
        self.fail_message = fail_message
        self.exception = None
        self.invoked = False
        self.skipped = False
    
    def run(self, step_definitions):
        self.invoked = True
        if step_definitions is None or step_definitions.skip_steps:
            self.skipped = True
        elif self.fail_message:
            step_definitions.skip_steps = True
            self.exception = Exception(self.fail_message)

# Tests.

class TestScenario(unittest.TestCase):
    def setUp(self):
        self.sc = Scenario(background=None, steps=[])
        self.listener = ListenerPlaceholder()
        event.add_listener(self.listener)
        self.step_definitions = StepDefinitionsPlaceholder()
    
    def tearDown(self):
        del(self.sc)
        del(self.listener)
        del(self.step_definitions)
    
    def test_000_default(self):
        self.assertTrue(self.sc.status is None)
        self.assertTrue(self.sc.exception is None)
    
    def test_001_zero_steps(self):
        self.sc.run(self.step_definitions)

        self.assertEqual(self.sc.status, 'passed')
        self.assertTrue(self.sc.exception is None)
        self.assertEqual(self.step_definitions.before_called, 1)
        self.assertEqual(self.step_definitions.after_called, 1)
    
    def test_002_one_step_passed(self):
        step = StepPlaceholder()
        self.sc.steps.append(step)
        self.sc.run(self.step_definitions)
        
        self.assertEqual(self.sc.status, 'passed')
        self.assertTrue(self.sc.exception is None)
        self.assertTrue(step.invoked)
        self.assertFalse(step.skipped)
        self.assertEqual(self.step_definitions.before_called, 1)
        self.assertEqual(self.step_definitions.after_called, 1)
    
    def test_003_one_step_failed(self):
        step = StepPlaceholder('failed step')
        self.sc.steps.append(step)
        self.sc.run(self.step_definitions)
        
        self.assertEqual(self.sc.status, 'failed')
        self.assertEqual(type(self.sc.exception), Exception)
        self.assertEqual(self.sc.exception.args, ('failed step',))
        self.assertTrue(step.invoked)
        self.assertFalse(step.skipped)
        self.assertEqual(self.step_definitions.before_called, 1)
        self.assertEqual(self.step_definitions.after_called, 1)
    
    def test_004_two_steps_passed(self):
        steps = [StepPlaceholder(), StepPlaceholder()]
        self.sc.steps.extend(steps)
        self.sc.run(self.step_definitions)
        
        self.assertEqual(self.sc.status, 'passed')
        self.assertTrue(self.sc.exception is None)
        self.assertTrue(steps[0].invoked and steps[1].invoked)
        self.assertFalse(steps[0].skipped or steps[1].skipped)
        self.assertEqual(self.step_definitions.before_called, 1)
        self.assertEqual(self.step_definitions.after_called, 1)

    def test_005_two_steps_failed_after_passed(self):
        steps = [StepPlaceholder(), StepPlaceholder('failed step')]
        self.sc.steps.extend(steps)
        self.sc.run(self.step_definitions)
        
        self.assertEqual(self.sc.status, 'failed')
        self.assertEqual(type(self.sc.exception), Exception)
        self.assertEqual(self.sc.exception.args, ('failed step',))
        self.assertTrue(steps[0].invoked and steps[1].invoked)
        self.assertFalse(steps[0].skipped or steps[1].skipped)
        self.assertEqual(self.step_definitions.before_called, 1)
        self.assertEqual(self.step_definitions.after_called, 1)

    def test_006_two_steps_failed_before_passed(self):
        steps = [StepPlaceholder('failed step'), StepPlaceholder()]
        self.sc.steps.extend(steps)
        self.sc.run(self.step_definitions)
        
        self.assertEqual(self.sc.status, 'failed')
        self.assertEqual(type(self.sc.exception), Exception)
        self.assertEqual(self.sc.exception.args, ('failed step',))
        self.assertTrue(steps[0].invoked and steps[1].invoked)
        self.assertTrue(not steps[0].skipped and steps[1].skipped)
        self.assertEqual(self.step_definitions.before_called, 1)
        self.assertEqual(self.step_definitions.after_called, 1)

    def test_007_two_steps_failed(self):
        steps = [StepPlaceholder('failed step'), StepPlaceholder('another failed step')]
        self.sc.steps.extend(steps)
        self.sc.run(self.step_definitions)
        
        self.assertEqual(self.sc.status, 'failed')
        self.assertEqual(type(self.sc.exception), Exception)
        self.assertEqual(self.sc.exception.args, ('failed step',))
        self.assertTrue(steps[0].invoked and steps[1].invoked)
        self.assertTrue(not steps[0].skipped and steps[1].skipped)
        self.assertEqual(self.step_definitions.before_called, 1)
        self.assertEqual(self.step_definitions.after_called, 1)

    def test_008_dry_run(self):
        self.step_definitions.dry_run = True
        step = StepPlaceholder()
        self.sc.steps.append(step)
        self.sc.run(self.step_definitions)
        
        self.assertEqual(self.sc.status, 'passed')
        self.assertTrue(self.sc.exception is None)
        self.assertTrue(step.invoked)
        self.assertTrue(step.skipped)
        self.assertEqual(self.step_definitions.before_called, 1)
        self.assertEqual(self.step_definitions.after_called, 1)
        
    def test_009_background_passed(self):
        self.sc.background = StepPlaceholder()
        step = StepPlaceholder()
        self.sc.steps.append(step)
        self.sc.run(self.step_definitions)
        
        self.assertEqual(self.sc.status, 'passed')
        self.assertTrue(self.sc.exception is None)
        self.assertTrue(self.sc.background.invoked)
        self.assertFalse(self.sc.background.skipped)
        self.assertTrue(step.invoked)
        self.assertFalse(step.skipped)
        self.assertEqual(self.step_definitions.before_called, 1)
        self.assertEqual(self.step_definitions.after_called, 1)
        
    def test_010_background_failed(self):
        self.sc.background = StepPlaceholder('failed background')
        step = StepPlaceholder()
        self.sc.steps.append(step)
        self.sc.run(self.step_definitions)
        
        self.assertEqual(self.sc.status, 'failed')
        self.assertEqual(type(self.sc.exception), Exception)
        self.assertEqual(self.sc.exception.args, ('failed background',))
        self.assertTrue(self.sc.background.invoked)
        self.assertFalse(self.sc.background.skipped)
        self.assertTrue(step.invoked)
        self.assertTrue(step.skipped)
        self.assertEqual(self.step_definitions.before_called, 1)
        self.assertEqual(self.step_definitions.after_called, 1)

    def test_011_none_step_definitions(self):
        self.sc.background = StepPlaceholder()
        step = StepPlaceholder()
        self.sc.steps.append(step)
        self.sc.run(None)
        
        self.assertEqual(self.sc.status, 'passed')
        self.assertTrue(self.sc.exception is None)
        self.assertTrue(self.sc.background.invoked)
        self.assertTrue(self.sc.background.skipped)
        self.assertTrue(step.invoked)
        self.assertTrue(step.skipped)
        self.assertEqual(self.step_definitions.before_called, 0)
        self.assertEqual(self.step_definitions.after_called, 0)


if __name__ == '__main__':
    unittest.main()
