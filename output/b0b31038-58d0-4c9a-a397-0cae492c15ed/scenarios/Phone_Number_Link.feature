Feature: Hover Interaction - Phone Number Link
  As a user visiting the website
  I want to see dropdown content when hovering over the phone number link
  So that I can access additional contact information

  @hover @dropdown
  Scenario: Phone number link reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "1-844-747-1620" phone number link
    Then a dropdown menu should become visible
    And I should see the following links:
      | Link Text | URL |
      | Learn More | https://alishasjourney.com/ |
      | 1-844-747-1620 | tel:18447471620 |
      | myjourney@mypatientstory.com | mailto:myjourney@mypatientstory.com |