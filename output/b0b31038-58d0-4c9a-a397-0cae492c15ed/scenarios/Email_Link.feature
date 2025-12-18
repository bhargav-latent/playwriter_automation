Feature: Hover Interaction - Email Link
  As a user visiting the website
  I want to see dropdown content when hovering over the email link
  So that I can access additional contact information

  @hover @dropdown
  Scenario: Email link reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "myjourney@mypatientstory.com" email link
    Then a dropdown menu should become visible
    And I should see the following links:
      | Link Text | URL |
      | Learn More | https://alishasjourney.com/ |
      | 1-844-747-1620 | tel:18447471620 |
      | myjourney@mypatientstory.com | mailto:myjourney@mypatientstory.com |