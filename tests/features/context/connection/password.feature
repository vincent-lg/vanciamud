Feature: test the connection.password context

  Scenario: connect to an existing user with a valid password
    Given a session on the 'connection.home' context
    And an account with the username 'kredh' and password 'manatee'
    When the user inputs 'kredh'
    And the user inputs 'manatee'
    Then the session is on the 'new.character.name' context
    And the account of username 'kredh' is linked to this session

  Scenario: connect to an existing user with a valid password
    Given a session on the 'connection.home' context
    And an account with the username 'kredh' and password 'manatee' and 3 characters
    When the user inputs 'kredh'
    And the user inputs 'manatee'
    Then the session is on the 'character.choice' context
    And the account of username 'kredh' is linked to this session

  Scenario: try to connect to an existing user with a wrong password
    Given a session on the 'connection.home' context
    And an account with the username 'kredh' and password 'manatee'
    When the user inputs 'kredh'
    And the user inputs 'Manatee'
    Then the session is on the 'connection.password' context
    And the account of username 'kredh' is linked to this session
