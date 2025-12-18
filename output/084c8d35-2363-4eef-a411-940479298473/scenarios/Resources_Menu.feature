Feature: Hover Interaction - Resources Menu
  As a user visiting the website
  I want to see dropdown content when hovering over the Resources menu
  So that I can access various resources

  @hover @dropdown
  Scenario: Resources menu reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "Resources" menu item
    Then a dropdown menu should become visible
    And I should see the following links:
      | Link Text | URL |
      | Blogs | /blog |
      | Use Cases | /comingsoon |
      | Embrace evolution with spiderAI™

Learn more | /blog/embracing-evolution-with-spider-ai |
      | View all resources | /blog |