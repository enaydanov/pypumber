from decorators import *

@Given(r'^passing$', table=multi)
def _(table):
    assert table.rows[0]['a'] == 'c' and table.rows[0]['b'] == 'd'

@Given(r'^failing$', string=multi)
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
    assert args[0].rows[0]['a'] == 'c'

@Given(r'^multiline plus keyword argument$')
def _(**kw):
    pass

@Given(r'^passing without a table$')
def _():
    pass

@Given(r'^failing without a table$')
def _():
    raise Exception('failing step')
