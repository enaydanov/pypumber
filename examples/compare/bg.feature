Feature: test background
  Background:
    Given I'm a cucumber
  
  Scenario: first scenario
    Given I'm a cucumber
    Given failing
    And failing
    
  Scenario: second scenario
    Given I'm a cucumber
    Then I'm a cucumber
  
  Scenario: with multiline
    Given multiline
      | a | b |
      | x | y |
