Feature: Failing background with scenario outlines sample

  Background:
    Given failing without a table

  Scenario Outline: failing background
    Then I should have '<count>' cukes
    Examples:
      |count|

  @tag1 @tag2
  Scenario Outline: another failing background
    Then I should have "<count>" cukes
    Examples:
      |count|
      | 10  |
      | 20  |
