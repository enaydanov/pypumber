#! /usr/bin/env python

import unittest, sys, os.path

if __name__ == '__main__':
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

import event

from gherkin.background import *

# Fixture placeholders.

class ListenerPlaceholder(object):
    def __call__(self, type, scenario):
        assert type == 'background'

class StepPlaceholder(object):
    def __init__(self, fail_message=None):
        self.fail_message = fail_message
        self.exception = None
        self.tb = None
        self.invoked = False
    
    def run(self, step_definitions):
        self.invoked = True
        if self.fail_message:
            self.exception = Exception(self.fail_message)
    
    def reset(self):
        pass

# Tests.

class TestBackground(unittest.TestCase):
    def setUp(self):
        self.bg = Background(steps=[])
        self.listener = ListenerPlaceholder()
        event.add_listener(self.listener)
    
    def tearDown(self):
        del(self.bg)
        del(self.listener)
    
    def test_000_default(self):
        self.assertTrue(self.bg.first_run)
        self.assertTrue(self.bg.exception is None)
    
    def test_001_zero_steps(self):
        self.bg.run(None)

        self.assertTrue(self.bg.exception is None)
        self.assertFalse(self.bg.first_run)
    
    def test_002_one_step_passed(self):
        step = StepPlaceholder()
        self.bg.steps.append(step)
        self.bg.run(None)
        
        self.assertTrue(self.bg.exception is None)
        self.assertTrue(step.invoked)
        self.assertFalse(self.bg.first_run)
    
    def test_003_one_step_failed(self):
        step = StepPlaceholder('failed step')
        self.bg.steps.append(step)
        self.bg.run(None)
        
        self.assertEqual(type(self.bg.exception), Exception)
        self.assertEqual(self.bg.exception.args, ('failed step',))
        self.assertFalse(self.bg.first_run)
        self.assertTrue(step.invoked)


if __name__ == '__main__':
    unittest.main()
