#! /usr/bin/env python

from decorators import *

instance = None

def getinstance():
    return instance

class Calculator(object):
    def __init__(self):
        self.args = []
    
    def push(self, a):
        self.args.append(a)
    
    def pop(self):
        return self.args.pop()

    @When(r'I add first and second', self=callback(getinstance))
    def add(self):
        b = self.args.pop()
        a = self.args.pop()
        self.push(a + b)

    @When(r'I substract first and second', self=callback(getinstance))
    def substract(self):
        b = self.args.pop()
        a = self.args.pop()
        self.push(a + b)

    @When(r'I multiply first and second', self=callback(getinstance))
    def multiply(self):
        b = self.args.pop()
        a = self.args.pop()
        self.push(a * b)

    @When(r'I divide first and second', self=callback(getinstance))
    def divide(self):
        b = self.args.pop()
        a = self.args.pop()
        self.push(a / b)

@Before
def _():
    global instance
    
    if instance is None:
        instance = Calculator()

@Given(r'^I take (\d+) and (\d+)$')
def _(a, b):
    instance.push(int(a))
    instance.push(int(b))

@Then(r'^I will see (\d+)$')
def _(result):
    assert int(result) == instance.pop()
