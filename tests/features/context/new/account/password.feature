Feature: test the new.account.password context

  Scenario: offer a strong enough password
    Given a session on the 'new.account.username' context
    When the user inputs 'administrator'
    When the user inputs 'ISee4Manatees'
    Then the session is on the 'new.account.confirm_password' context

  Scenario: try to enter a too-short password
    Given a session on the 'new.account.username' context
    When the user inputs 'administrator'
    And the user inputs 'a'
    Then the session is on the 'new.account.password' context
