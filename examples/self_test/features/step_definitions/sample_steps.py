from decorators import *

def flunker():
    raise "FAIL"

@Given(r'^passing$', table=multi)
def _(table):
    pass

@Given(r'^failing$', string=multi)
def _(string):
    flunker()

@Given(r'^passing without a table$')
def _():
    pass

@Given(r'^failing without a table$')
def _():
    flunker()

@Given(r'^a step definition that calls an undefined step$')
def _():
    given('this does not exist')

@Given(r'^call step "(.*)"$')
def _(step):
    given(step)

@Given(r"^'(.+)' cukes$")
def _(cukes):
    world.cukes = cukes

@Then(r"^I should have '(.+)' cukes$")
def _(cukes):
    assert world.cukes.value() == cukes

@Given(r"^'(.+)' global cukes$")
def _(cukes):
    if 'scenario_runs' not in universe:
        universe.scenario_runs = 0
    
    if universe.scenario_runs.value() >= 1:
        flunker()
    
    universe.cukes = cukes
    universe.scenario_runs = universe.scenario_runs.value() + 1

@Then(r"^I should have '(.+)' global cukes$")
def _(cukes):
    assert universe.cukes.value() == cukes

@Given(r'^table$', table=multi)
def _(table):
    world.table = table

@Given(r'^multiline string$', string=multi)
def _(string):
    world.multiline = string

@Then(r'^the table should be$', table=multi)
def _(table):
    assert repr(world.table.value()) == repr(table)

@Then(r'^the multiline string should be$', string=multi)
def _(string):
    world.multiline.value() == string

@Given(r'^failing expectation$')
def _():
    assert 'this' == 'that'

@Given(r'^unused$')
def _():
    pass

@Given(r'^another unused$')
def _():
    pass
