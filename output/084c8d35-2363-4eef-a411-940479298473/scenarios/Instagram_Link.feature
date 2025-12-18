Feature: Hover Interaction - Instagram Link
  As a user visiting the website
  I want to see dropdown content when hovering over the Instagram link
  So that I can access navigation links

  @hover @dropdown
  Scenario: Instagram link reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "Instagram" link
    Then a dropdown menu should become visible
    And I should see the following links:
      | Link Text | URL |
      | Home | / |
      | spiderAI™ | /spiderai |
      | iHz™ | /ihz |
      | About | /about |
      | Blog | /blog |
      | Contact Us | /contactus |
      | Facebook | https://www.facebook.com/profile.php?id=100042907616152 |
      | Instagram | https://www.instagram.com/inside_minto.ai/ |
      | Twitter | https://x.com/mintoai_iiot?lang=en |
      | LinkedIn | https://in.linkedin.com/company/mintoai |