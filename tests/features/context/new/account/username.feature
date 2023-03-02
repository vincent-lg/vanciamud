Feature: test the new.account.username context

  Scenario: create a valid account
    Given a session on the 'new.account.username' context
    When the user inputs 'administrator'
    Then the session is on the 'new.account.password' context

  Scenario: try to create an account with an existing username
    Given a session on the 'new.account.username' context
    And an account with the username 'administrator'
    When the user inputs 'administrator'
    Then the session is on the 'new.account.username' context

  Scenario: create a valid account while another account exists
    Given a session on the 'new.account.username' context
    And an account with the username 'administrator'
    When the user inputs 'kredh'
    Then the session is on the 'new.account.password' context

  Scenario: try to create an account with an invalid username
    Given a session on the 'new.account.username' context
    When the user inputs 'test'
    Then the session is on the 'new.account.username' context

  Scenario: try to create an account with a short name
    Given a session on the 'new.account.username' context
    When the user inputs 'a'
    Then the session is on the 'new.account.username' context
