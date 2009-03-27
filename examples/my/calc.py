#! /usr/bin/env python

from decorators import *

class Calculator(object):
    def __init__(self):
        self.args = []
    
    def push(self, a):
        self.args.append(a)
    
    def pop(self):
        return self.args.pop()
    
    def add(self):
        b = self.args.pop()
        a = self.args.pop()
        self.push(a + b)

    def substract(self):
        b = self.args.pop()
        a = self.args.pop()
        self.push(a + b)

    def multiply(self):
        b = self.args.pop()
        a = self.args.pop()
        self.push(a * b)

    def divide(self):
        b = self.args.pop()
        a = self.args.pop()
        self.push(a / b)

instance = None

@Before
def _():
    global instance
    
    if instance is None:
        instance = Calculator()

@Given(r'^I take (\d+) and (\d+)$')
def _(a, b):
    instance.push(int(a))
    instance.push(int(b))

@When(r'I add first and second')
def _():
    instance.add()

@Then(r'^I will see (\d+)$')
def _(result):
    assert int(result) == instance.pop()
