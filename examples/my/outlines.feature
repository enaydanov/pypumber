Feature: Complex feature with Background, Scenario Outlines and 
  multiline arguments.
  
  @outline
  Scenario Outline: Without multilne
    Given I take <one> and <two>
    When I <operation> first and second
    Then I will see <result>
  
  Examples: Ariphmetic
    | one | two | operation | result  |
    |  3  |  3  | add       |    6    |
    |  3  |  3  | substract |    0    |
    |  3  |  3  | multiply  |    9    |
    |  3  |  3  | divide    |    1    |
    |  a  |  b  |           | unknown |
  
  Scenario Outline: With pystring
    Given go to <page>
    When I click <button>
    Then I will see following message:
    """
      Button '<button>' is pressed.
    """
  
  Examples:
    | page  | button | 
    | site1 |  Ok     |
    | site2 | Cancel |
    | site3 | Don't push this button |
  
  Scenario Outline: With table
    Given Following acounts exist:
      | <login> | <password> |
      |  aa     | aa |
      |  bb     | bb |
    When Try to login
    Then access granted
    
  Examples:
    | login | password |
    | login | passwd |
    | user  | pass |

  Scenario Outline: Unused column
    Given something
  
  Examples:
    | unused |
    |  a     |
    |  b     |
