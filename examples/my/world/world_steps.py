from decorators import *

@Given(r"^I'm a cucumber$")
def _():
    world.cuke = Cucumber()

@Given(r"^I'm a cucumber from outter space$")
def _():
    universe.cuke = Cucumber()

class Cucumber(object):
    def __init__(self):
        self.spines = 'big'
        self.age = 0

    @Given(r'^passing$', self=world.cuke)
    @Given(r'^passing universe$', self=universe.cuke)
    def passing(self):
        assert self.spines == 'big'

    @Given(r'^failing$', self=world.cuke)
    @Given(r'^failing universe$', self=universe.cuke)
    def failing(self):
        raise Exception('failing step')

    @When(r"^I'll grow during (\d+) days$", self=universe.cuke)
    @cast(d=int)
    def grow(self, d):
        self.age += d
    
    @Then(r'^I have length (\d+(.\d*)?) cm$', 'length', self=universe.cuke)
    @cast(length=float)
    @assert_returns('length')
    def get_length(self):
        """We have a cucumbers that grow by 0.1 cm each day"""
        return self.age * 0.1
        
@Given(r"^I'm a super cucumber$")
@Given(r"^I'm a (.+) cucumber$")
def _(*args):
    pass
