@one
Feature: Sample

    @two @three
  Scenario: Missing
    Given missing

@three
  Scenario: Passing
    Given passing
      |a|b|
      |c|d|
  
  @four
  Scenario: Failing
    Given failing
      """
      hello
      """

  Scenario: Pending
    Given some pending step 5
    And another pending step 6

  Scenario: Multiline
    Given multiline plus positional argument
      |a|b|
      |c|d|