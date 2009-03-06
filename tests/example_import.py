#!/usr/bin/env python

from decorators import Given, Then, When

@Given(r'some string')
def tmp():
    return "tmp"
