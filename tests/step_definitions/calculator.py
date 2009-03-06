#! /usr/bin/env python

from decorators import Given, When, Then

class Calculator:
    def __init__(self):
        self.args = {}
        
    def put(self, reg, x):
        self.args[reg] = x
        
    def sum(self):
        self.result = self.args['first'] + self.args['second']

    def show(self):
        return 'Answer: %d' % self.result

instance = None

@Given(r'I visit the calculator page')
def _():
    global instance
    
    instance = Calculator()

@Given(r"I fill in '(\d+)' for '(\w+)'")
def _(x, reg):
    instance.put(reg, int(x))
    
@When(r"I press 'Add'")
def _():
    instance.sum()

@Then(r"I should see '(.*)'")
def _(s):
    assert instance.show() == s
