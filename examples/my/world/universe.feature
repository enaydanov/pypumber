Feature: Cucumber from Outter Space

  Scenario: Creating
    Given I'm a cucumber from outter space
  
  Scenario: Growing
    Given I'm a cucumber from outter space
    When I'll grow during 5 days
    Then I have length 0.5 cm
  
  Scenario: And Growing
    When I'll grow during 5 days
    Then I have length 1 cm
  
  Scenario: Failing
    Then I have length 0 cm

