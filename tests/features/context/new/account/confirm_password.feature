Feature: test the new.account.confirm_password context

  Scenario: offer a strong enough password twice
    Given a session on the 'new.account.username' context
    When the user inputs 'administrator'
    And the user inputs 'ISee4Manatees'
    And the user inputs 'ISee4Manatees'
    Then the session is on the 'new.account.email' context

  Scenario: fail to repeat the same password twice
    Given a session on the 'new.account.username' context
    When the user inputs 'administrator'
    And the user inputs 'ISee4Manatees'
    And the user inputs 'ISee3Manatees'
    Then the session is on the 'new.account.password' context
