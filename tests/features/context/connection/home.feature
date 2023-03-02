Feature: test the connection.home context

  Scenario: try to create a new user account
    Given a session on the 'connection.home' context
    When the user inputs 'new'
    Then the session is on the 'new.account.username' context
    But no account is linked to this session

  Scenario: try to login to an existing account
    Given a session on the 'connection.home' context
    And an account with the username 'kredh'
    When the user inputs 'kredh'
    Then the session is on the 'connection.password' context
    And the account of username 'kredh' is linked to this session

  Scenario: try to login to an nonexistant account
    Given a session on the 'connection.home' context
    When the user inputs 'kredh'
    Then the session is on the 'connection.home' context
    But no account is linked to this session

  Scenario: try to login to an nonexistant account with another existent account
    Given a session on the 'connection.home' context
    And an account with the username 'mark'
    When the user inputs 'kredh'
    Then the session is on the 'connection.home' context
    But no account is linked to this session
