Feature: Hover Interaction - Products Menu
  As a user visiting the website
  I want to see dropdown content when hovering over the Products menu
  So that I can access product categories

  @hover @dropdown
  Scenario: Products menu reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "Products" menu item
    Then a dropdown menu should become visible
    And I should see the following links:
      | Link Text | URL |
      | iHz™ - IoT system for Electrical Signature analysi | /ihz |
      | spiderAI™ - Operational intelligence platform for  | /spiderai |