Feature: Passing background with multiline args

  Background:
    Given table
      |a|b|e|
      |c|d|f|
    And multiline string
    """
      I'm a cucumber and I'm okay. 
      I sleep all night and I test all day
    """

  Scenario: passing background
    Then the table should be
      |a|b|
      |c|d|
    Then the multiline string should be
    """
      I'm a cucumber and I'm okay. 
      I sleep all night and I test all day
    """

  Scenario: another passing background
    Then the table should be
      |a|b|
      |c|d|
    Then the multiline string should be
    """
      I'm a cucumber and I'm okay. 
      I sleep all night and I test all day
    """
    
  Scenario: without multi
    Then the table should be
    Then the multiline string should be

  Scenario: empty cells
    Then the table should be
       |a|b|
       |||
    Then the multiline string should be
