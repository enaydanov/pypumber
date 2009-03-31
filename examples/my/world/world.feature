Feature: Cucumber World
  Background:
    Given I'm a cucumber

  Scenario: failing
    Given failing
  
  @passing
  Scenario: passing
    Given passing
  
  Scenario: missing
    Given missing
    
  Scenario: skipped
    Given failing
    Given skipped

  Scenario Outline: all
    Given <state>
    
    Examples:
      | state |
      | passing |
      | failing |
      | missing |
