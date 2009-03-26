from decorators import *

@Given(r'^passing$')
def _(table):
    assert table[1]['a'] == 'c' and table[1]['b'] == 'd'

@Given(r'^failing$')
def _(string):
    assert len(string) == 1

@Given(r'^some pending step (\d+)$')
@pending
def _(x):
   raise Exception
   pending()

@pending.Given(r'^another pending step (\d+)$')
def _(x):
   raise Exception()

@Given(r'^multiline plus positional argument$')
def _(*args):
    assert args[0][1]['a'] == 'c'

@Given(r'^multiline plus keyword argument$')
def _(**kw):
    pass
