@feature_tag
Feature: Addition
  In order to avoid silly mistakes
  As a math idiot 
  I want to be told the sum of two numbers

  @sometag @someanothertag
  Scenario: Add two numbers
    Given I visit the calculator page
    And I fill in '50' for 'first'
    And I fill in '70' for 'second'
    When I press 'Add'
    Then I should see 'Answer: 120'

  Scenario: Add another two numbers
    Given I visit the calculator page
    And I fill in '20' for 'first'
    And I fill in '666' for 'second'
    When I press 'Substract'
      |a|b|
      |1|2|
      |3|4|
    Then I should see 'Answer: -10'
    """
       Some multiline string
    """
