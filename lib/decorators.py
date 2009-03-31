#!/usr/bin/env python

class _Placeholder(object):
    def __getattr__(*args):
        pass
    
    def __call__(*args, **kwargs):
        return lambda fn: fn
    
Given = _Placeholder()

When = Given
Then = Given
pending = Given
cast = Given
assert_returns = Given
universe = Given
world = Given

Before = Given()

After = Before
AfterStep = Before
callback = Before
multi = None
