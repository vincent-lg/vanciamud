Feature: test the new.player.name context

  Scenario: create a valid player in a new account
    Given a session on the 'new.account.username' context
    When the user inputs 'administrator'
    And the user inputs 'ISee4Manatees'
    And the user inputs 'ISee4Manatees'
    And the user inputs 'kredh@mail.com'
    And the user inputs 'Camilla'
    Then the session is on the 'connection.game' context
