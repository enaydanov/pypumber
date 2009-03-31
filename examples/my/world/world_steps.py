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
    
    @Given(r"^I'm is (\d+) days old$", self=world.cuke)
    @When(r"^I'm is (\d+) days old$", self=universe.cuke)
    @cast(d=int)
    def set_age(self, d):
        assert d < 100000, 'this is very wrong age for cucumber'
        self.age = d
    
    @Then(r'^I have length (\d+(.\d*)?) cm$', 'length', self=universe.cuke)
    @cast(length=float)
    @assert_returns('length')
    def get_length(self):
        """We have a cucumbers that grow by 0.1 cm each day"""
        return self.age * 0.1
    
    @Then(r'^I have (?P<color>.*) color$', self=world.cuke)
    @assert_returns('color')
    def get_color(self):
        if self.age < 50:
            return 'darkgreen'
        elif 50 < self.age < 100:
            return 'green'
        elif 100 < self.age < 1000:
            return 'yellow'
        else:
            return 'black'

@Given(r"^I'm a super cucumber$")
@Given(r"^I'm a (.+) cucumber$")
def _(*args):
    pass
