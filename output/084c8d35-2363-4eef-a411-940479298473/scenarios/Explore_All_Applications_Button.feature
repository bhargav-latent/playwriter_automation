Feature: Hover Interaction - Explore All Applications Button
  As a user visiting the website
  I want to see additional content when hovering over the Explore All Applications button
  So that I can access more application options

  @hover @content_revealed
  Scenario: Explore All Applications button reveals additional content on hover
    Given I am on the homepage
    When I hover over the "Explore All Applications" button
    Then additional content should become visible
    And I should see the following elements:
      | Element Type | Description |
      | BUTTON | Additional application buttons |