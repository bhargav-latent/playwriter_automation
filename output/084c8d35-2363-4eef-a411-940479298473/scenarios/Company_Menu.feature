Feature: Hover Interaction - Company Menu
  As a user visiting the website
  I want to see dropdown content when hovering over the Company menu
  So that I can access company-related information

  @hover @dropdown
  Scenario: Company menu reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "Company" menu item
    Then a dropdown menu should become visible
    And I should see the following links:
      | Link Text | URL |
      | About us | /about |
      | Careers | /careers |
      | Contact | /contactus |
      | Looking for a new career? Get in touch | /contactus |