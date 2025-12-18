Feature: Hover Interaction - Study Results Link
  As a user visiting the website
  I want to see dropdown content when hovering over the Study Results link
  So that I can access related information

  @hover @dropdown
  Scenario: Study Results link reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "Study Results" link
    Then a dropdown menu should become visible
    And I should see the following links:
      | Link Text | URL |
      | Study Results | /study-results/ |
      | Learn More | /study-results/ |
      | Safety | /safety-and-side-effects/ |