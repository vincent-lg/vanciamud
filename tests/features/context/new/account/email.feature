Feature: test the new.account.email context

  Scenario: enter a valid email address
    Given a session on the 'new.account.username' context
    When the user inputs 'administrator'
    And the user inputs 'ISee4Manatees'
    And the user inputs 'ISee4Manatees'
    And the user inputs 'kredh@mail.com'
    Then the session is on the 'new.character.name' context
    And an account exists with username 'administrator' and password 'ISee4Manatees' and email 'kredh@mail.com'

  Scenario: enter a non-valid email address
    Given a session on the 'new.account.username' context
    When the user inputs 'administrator'
    And the user inputs 'ISee4Manatees'
    And the user inputs 'ISee4Manatees'
    And the user inputs 'kredh'
    Then the session is on the 'new.account.email' context

  Scenario: enter a valid email address
    Given a session on the 'new.account.username' context
    When the user inputs 'administrator'
    And the user inputs 'ISee4Manatees'
    And the user inputs 'ISee4Manatees'
    And the user inputs 'no'
    Then the session is on the 'new.character.name' context
    And an account exists with username 'administrator' and password 'ISee4Manatees' and no email
