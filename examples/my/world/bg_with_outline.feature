Feature: Cucumber World
  Background:
    Given I'm a cucumber

  Scenario Outline: Cucumber Colors
    Given I'm a cucumber
    And I'm is <days> days old
    Then I have <color> color 
    
    Examples:
      | days | color |
      | 0 | darkgreen |
      | 10 | darkgreen |
      | 50 | darkgreen |
      | 60 | green |
      | 100 | green |
      | 1000 | black |
      | 999 | red |
      |100000| |
