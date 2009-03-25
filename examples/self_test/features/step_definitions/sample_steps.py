from decorators import *

@Given(r'^passing$')
def _(table):
    assert table[1]['a'] == 'c' and table[1]['b'] == 'd'

@Given(r'^failing$')
def _(string):
    assert len(string) == 1
