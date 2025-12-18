Feature: Hover Interaction - About Tivdak Menu
  As a user visiting the website
  I want to see dropdown content when hovering over the About Tivdak menu
  So that I can access information about Tivdak

  @hover @dropdown
  Scenario: About Tivdak menu reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "About Tivdak" menu item
    Then a dropdown menu should become visible
    And I should see the following links:
      | Link Text | URL |
      | Tivdak and You | /about-tivdak/ |
      | What Is Tivdak? | /about-tivdak/ |