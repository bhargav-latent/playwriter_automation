Feature: Hover Interaction - Privacy Policy Menu
  As a user visiting the website
  I want to see dropdown content when hovering over the Privacy Policy link
  So that I can access privacy-related information

  @hover @dropdown
  Scenario: Privacy Policy link reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "Privacy Policy" link
    Then a dropdown menu should become visible
    And I should see the following links:
      | Link Text | URL |
      | 1-800-FDA-1088 | tel:1-800-332-1088 |
      | full Prescribing Information | https://labeling.pfizer.com/ShowLabeling.aspx?id=20632 |
      | Medication Guide | https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide |
      | Terms of Use | https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf |
      | Privacy Policy | https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf |
      | Sitemap | /sitemap/ |
      | Contact Us | https://www.pfizer.com/contact |
      | | https://www.pfizer.com/ |
      | | https://www.genmab.com/ |