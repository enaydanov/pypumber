#!/usr/bin/env python

def Given(*args, **kwargs):
    return lambda fn: fn
    
When = Given
Then = Given

def Before(fn):
    return fn

After = Before
AfterStep = Before

#pending

multi = None

def callback(*args, **kwargs):
    pass
