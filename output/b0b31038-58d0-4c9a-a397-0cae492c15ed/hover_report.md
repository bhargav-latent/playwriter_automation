# Hover Detection Report for Tivdak

Generated: 2025-12-18 15:40:26
Session ID: `b0b31038-58d0-4c9a-a397-0cae492c15ed`

---

## TLDR - Executive Summary

**Website:** Tivdak
**Test Date:** 2025-12-18 15:40
**Session ID:** `b0b31038-58d0-4c9a-a397-0cae492c15ed`

### At a Glance

| Metric | Value |
|--------|-------|
| Total Elements Tested | 23 |
| Interactive Elements Found | 12 |
| Test Success Rate | 87.0% |
| Gherkin Scenarios Generated | 12 |

### Key Findings

**✅ Dropdowns Detected (12):**
  - **Click to expand About Tivdak menu**: reveals 2 links
  - **Learn More link**: reveals 3 links
  - **Phone number link**: reveals 3 links
  - **Email link**: reveals 3 links
  - **Study Results link**: reveals 3 links

**ℹ️ Static Elements (8):** Elements with no hover behavior (click-only)

**ℹ️ Unreachable Elements (3):** Elements that could not be hovered (out of viewport, hidden, or dynamically loaded)
  - Click to expand Results menu
  - Click to expand What to Expect menu
  - Click to expand Support menu

### Insights

- The site has **12 interactive hover elements** that enhance user navigation
- Dropdown menus reveal a total of **69 navigation links**
- **3 elements** were unreachable (out of viewport, hidden, or dynamically loaded - this is expected for modern dynamic websites)
- **Good test coverage** - most elements were successfully tested

---

## Table of Contents

1. [TLDR - Executive Summary](#tldr---executive-summary)
2. [Test Scenarios with Evidence](#test-scenarios-with-evidence)
3. [Summary](#summary)

---

## Test Scenarios with Evidence

Each scenario includes the Gherkin specification followed by before/after screenshot comparison.

### About Tivdak Menu

**Behavior Detected:** `dropdown`
**Scenario File:** `scenarios/About_Tivdak_Menu.feature`

```gherkin
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
```

#### Screenshot Evidence

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/001_Click_to_expand_About_Tivdak_m_before.png) | ![After](screenshots/002_Click_to_expand_About_Tivdak_m_after.png) |

#### Revealed Links

- [Tivdak and You](/about-tivdak/)
- [What Is Tivdak?](/about-tivdak/)

---

### Contact Us Link

**Behavior Detected:** `dropdown`
**Scenario File:** `scenarios/Contact_Us_Link.feature`

```gherkin
Feature: Hover Interaction - Contact Us Link
  As a user visiting the website
  I want to see dropdown content when hovering over the Contact Us link
  So that I can access related information

  @hover @dropdown
  Scenario: Contact Us link reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "Contact Us" link
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
```

#### Screenshot Evidence

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/040_Contact_Us_link_before.png) | ![After](screenshots/041_Contact_Us_link_after.png) |

#### Revealed Links

- [1-800-FDA-1088](tel:1-800-332-1088)
- [full Prescribing Information](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632)
- [Medication Guide](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide)
- [Terms of Use](https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf)
- [Privacy Policy](	
                            https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf)

---

### Email Link

**Behavior Detected:** `dropdown`
**Scenario File:** `scenarios/Email_Link.feature`

```gherkin
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
```

#### Screenshot Evidence

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/024_Email_link_before.png) | ![After](screenshots/025_Email_link_after.png) |

#### Revealed Links

- [Learn More](https://alishasjourney.com/)
- [1-844-747-1620](tel:18447471620)
- [myjourney@mypatientstory.com](mailto:myjourney@mypatientstory.com)

---

### FDA Reporting Number Link

**Behavior Detected:** `dropdown`
**Scenario File:** `scenarios/FDA_Reporting_Number_Link.feature`

```gherkin
Feature: Hover Interaction - FDA Reporting Number Link
  As a user visiting the website
  I want to see dropdown content when hovering over the FDA reporting number link
  So that I can access related information

  @hover @dropdown
  Scenario: FDA reporting number link reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "1-800-FDA-1088" link
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
```

#### Screenshot Evidence

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/028_FDA_reporting_number_link_before.png) | ![After](screenshots/029_FDA_reporting_number_link_after.png) |

#### Revealed Links

- [1-800-FDA-1088](tel:1-800-332-1088)
- [full Prescribing Information](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632)
- [Medication Guide](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide)
- [Terms of Use](https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf)
- [Privacy Policy](	
                            https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf)

---

### Full Prescribing Information Link

**Behavior Detected:** `dropdown`
**Scenario File:** `scenarios/Full_Prescribing_Information_Link.feature`

```gherkin
Feature: Hover Interaction - Full Prescribing Information Link
  As a user visiting the website
  I want to see dropdown content when hovering over the Full Prescribing Information link
  So that I can access related information

  @hover @dropdown
  Scenario: Full Prescribing Information link reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "full Prescribing Information" link
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
```

#### Screenshot Evidence

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/030_Full_Prescribing_Information_l_before.png) | ![After](screenshots/031_Full_Prescribing_Information_l_after.png) |

#### Revealed Links

- [1-800-FDA-1088](tel:1-800-332-1088)
- [full Prescribing Information](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632)
- [Medication Guide](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide)
- [Terms of Use](https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf)
- [Privacy Policy](	
                            https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf)

---

### Learn More Link

**Behavior Detected:** `dropdown`
**Scenario File:** `scenarios/Learn_More_Link.feature`

```gherkin
Feature: Hover Interaction - Learn More Link
  As a user visiting the website
  I want to see dropdown content when hovering over the Learn More link
  So that I can access additional resources

  @hover @dropdown
  Scenario: Learn More link reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "Learn More" link
    Then a dropdown menu should become visible
    And I should see the following links:
      | Link Text | URL |
      | Learn More | https://alishasjourney.com/ |
      | 1-844-747-1620 | tel:18447471620 |
      | myjourney@mypatientstory.com | mailto:myjourney@mypatientstory.com |
```

#### Screenshot Evidence

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/020_Learn_More_link_before.png) | ![After](screenshots/021_Learn_More_link_after.png) |

#### Revealed Links

- [Learn More](https://alishasjourney.com/)
- [1-844-747-1620](tel:18447471620)
- [myjourney@mypatientstory.com](mailto:myjourney@mypatientstory.com)

---

### Phone Number Link

**Behavior Detected:** `dropdown`
**Scenario File:** `scenarios/Phone_Number_Link.feature`

```gherkin
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
```

#### Screenshot Evidence

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/022_Phone_number_link_before.png) | ![After](screenshots/023_Phone_number_link_after.png) |

#### Revealed Links

- [Learn More](https://alishasjourney.com/)
- [1-844-747-1620](tel:18447471620)
- [myjourney@mypatientstory.com](mailto:myjourney@mypatientstory.com)

---

### Privacy Policy Link

**Behavior Detected:** `dropdown`
**Scenario File:** `scenarios/Privacy_Policy_Link.feature`

```gherkin
Feature: Hover Interaction - Privacy Policy Link
  As a user visiting the website
  I want to see dropdown content when hovering over the Privacy Policy link
  So that I can access related information

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
```

#### Screenshot Evidence

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/036_Privacy_Policy_link_before.png) | ![After](screenshots/037_Privacy_Policy_link_after.png) |

#### Revealed Links

- [1-800-FDA-1088](tel:1-800-332-1088)
- [full Prescribing Information](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632)
- [Medication Guide](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide)
- [Terms of Use](https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf)
- [Privacy Policy](	
                            https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf)

---

### Sitemap Link

**Behavior Detected:** `dropdown`
**Scenario File:** `scenarios/Sitemap_Link.feature`

```gherkin
Feature: Hover Interaction - Sitemap Link
  As a user visiting the website
  I want to see dropdown content when hovering over the Sitemap link
  So that I can access related information

  @hover @dropdown
  Scenario: Sitemap link reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "Sitemap" link
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
```

#### Screenshot Evidence

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/038_Sitemap_link_before.png) | ![After](screenshots/039_Sitemap_link_after.png) |

#### Revealed Links

- [1-800-FDA-1088](tel:1-800-332-1088)
- [full Prescribing Information](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632)
- [Medication Guide](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide)
- [Terms of Use](https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf)
- [Privacy Policy](	
                            https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf)

---

### Study Results Link

**Behavior Detected:** `dropdown`
**Scenario File:** `scenarios/Study_Results_Link.feature`

```gherkin
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
```

#### Screenshot Evidence

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/026_Study_Results_link_before.png) | ![After](screenshots/027_Study_Results_link_after.png) |

#### Revealed Links

- [Study Results](/study-results/)
- [Learn More](/study-results/)
- [Safety](/safety-and-side-effects/)

---

### Terms of Use Link

**Behavior Detected:** `dropdown`
**Scenario File:** `scenarios/Terms_of_Use_Link.feature`

```gherkin
Feature: Hover Interaction - Terms of Use Link
  As a user visiting the website
  I want to see dropdown content when hovering over the Terms of Use link
  So that I can access related information

  @hover @dropdown
  Scenario: Terms of Use link reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "Terms of Use" link
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
```

#### Screenshot Evidence

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/034_Terms_of_Use_link_before.png) | ![After](screenshots/035_Terms_of_Use_link_after.png) |

#### Revealed Links

- [1-800-FDA-1088](tel:1-800-332-1088)
- [full Prescribing Information](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632)
- [Medication Guide](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide)
- [Terms of Use](https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf)
- [Privacy Policy](	
                            https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf)

---

### Your Privacy Choices Link

**Behavior Detected:** `dropdown`
**Scenario File:** `scenarios/Your_Privacy_Choices_Link.feature`

```gherkin
Feature: Hover Interaction - Your Privacy Choices Link
  As a user visiting the website
  I want to see dropdown content when hovering over the Your Privacy Choices link
  So that I can access related information

  @hover @dropdown
  Scenario: Your Privacy Choices link reveals dropdown on hover
    Given I am on the homepage
    When I hover over the "Your Privacy Choices" link
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
```

#### Screenshot Evidence

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/042_Your_Privacy_Choices_link_before.png) | ![After](screenshots/043_Your_Privacy_Choices_link_after.png) |

#### Revealed Links

- [1-800-FDA-1088](tel:1-800-332-1088)
- [full Prescribing Information](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632)
- [Medication Guide](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide)
- [Terms of Use](https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf)
- [Privacy Policy](	
                            https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf)

---

## Additional Interactive Elements

These interactive hover elements were detected but don't have individual scenario files.

### Click to expand About Tivdak menu

**Behavior:** `dropdown`

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/001_Click_to_expand_About_Tivdak_m_before.png) | ![After](screenshots/002_Click_to_expand_About_Tivdak_m_after.png) |

#### Revealed Links

- [Tivdak and You](/about-tivdak/)
- [What Is Tivdak?](/about-tivdak/)

---

### Learn More link

**Behavior:** `dropdown`

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/020_Learn_More_link_before.png) | ![After](screenshots/021_Learn_More_link_after.png) |

#### Revealed Links

- [Learn More](https://alishasjourney.com/)
- [1-844-747-1620](tel:18447471620)
- [myjourney@mypatientstory.com](mailto:myjourney@mypatientstory.com)

---

### Phone number link

**Behavior:** `dropdown`

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/022_Phone_number_link_before.png) | ![After](screenshots/023_Phone_number_link_after.png) |

#### Revealed Links

- [Learn More](https://alishasjourney.com/)
- [1-844-747-1620](tel:18447471620)
- [myjourney@mypatientstory.com](mailto:myjourney@mypatientstory.com)

---

### Email link

**Behavior:** `dropdown`

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/024_Email_link_before.png) | ![After](screenshots/025_Email_link_after.png) |

#### Revealed Links

- [Learn More](https://alishasjourney.com/)
- [1-844-747-1620](tel:18447471620)
- [myjourney@mypatientstory.com](mailto:myjourney@mypatientstory.com)

---

### Study Results link

**Behavior:** `dropdown`

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/026_Study_Results_link_before.png) | ![After](screenshots/027_Study_Results_link_after.png) |

#### Revealed Links

- [Study Results](/study-results/)
- [Learn More](/study-results/)
- [Safety](/safety-and-side-effects/)

---

### FDA reporting number link

**Behavior:** `dropdown`

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/028_FDA_reporting_number_link_before.png) | ![After](screenshots/029_FDA_reporting_number_link_after.png) |

#### Revealed Links

- [1-800-FDA-1088](tel:1-800-332-1088)
- [full Prescribing Information](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632)
- [Medication Guide](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide)
- [Terms of Use](https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf)
- [Privacy Policy](	
                            https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf)

---

### Full Prescribing Information link

**Behavior:** `dropdown`

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/030_Full_Prescribing_Information_l_before.png) | ![After](screenshots/031_Full_Prescribing_Information_l_after.png) |

#### Revealed Links

- [1-800-FDA-1088](tel:1-800-332-1088)
- [full Prescribing Information](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632)
- [Medication Guide](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide)
- [Terms of Use](https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf)
- [Privacy Policy](	
                            https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf)

---

### Terms of Use link

**Behavior:** `dropdown`

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/034_Terms_of_Use_link_before.png) | ![After](screenshots/035_Terms_of_Use_link_after.png) |

#### Revealed Links

- [1-800-FDA-1088](tel:1-800-332-1088)
- [full Prescribing Information](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632)
- [Medication Guide](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide)
- [Terms of Use](https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf)
- [Privacy Policy](	
                            https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf)

---

### Privacy Policy link

**Behavior:** `dropdown`

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/036_Privacy_Policy_link_before.png) | ![After](screenshots/037_Privacy_Policy_link_after.png) |

#### Revealed Links

- [1-800-FDA-1088](tel:1-800-332-1088)
- [full Prescribing Information](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632)
- [Medication Guide](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide)
- [Terms of Use](https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf)
- [Privacy Policy](	
                            https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf)

---

### Sitemap link

**Behavior:** `dropdown`

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/038_Sitemap_link_before.png) | ![After](screenshots/039_Sitemap_link_after.png) |

#### Revealed Links

- [1-800-FDA-1088](tel:1-800-332-1088)
- [full Prescribing Information](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632)
- [Medication Guide](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide)
- [Terms of Use](https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf)
- [Privacy Policy](	
                            https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf)

---

### Contact Us link

**Behavior:** `dropdown`

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/040_Contact_Us_link_before.png) | ![After](screenshots/041_Contact_Us_link_after.png) |

#### Revealed Links

- [1-800-FDA-1088](tel:1-800-332-1088)
- [full Prescribing Information](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632)
- [Medication Guide](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide)
- [Terms of Use](https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf)
- [Privacy Policy](	
                            https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf)

---

### Your Privacy Choices link

**Behavior:** `dropdown`

| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before](screenshots/042_Your_Privacy_Choices_link_before.png) | ![After](screenshots/043_Your_Privacy_Choices_link_after.png) |

#### Revealed Links

- [1-800-FDA-1088](tel:1-800-332-1088)
- [full Prescribing Information](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632)
- [Medication Guide](https://labeling.pfizer.com/ShowLabeling.aspx?id=20632&Section=MedGuide)
- [Terms of Use](https://webfiles.pfizer.com/Seagen_Terms_and_Conditions.pdf)
- [Privacy Policy](	
                            https://webfiles.pfizer.com/Seagen_Privacy_Policy.pdf)

---

## Summary

| Metric | Count |
|--------|-------|
| Total elements tested | 23 |
| Dropdowns detected | 12 |
| Tooltips detected | 0 |
| Content revealed | 0 |
| No change | 8 |
| Unreachable | 3 |
| Scenario files generated | 12 |

### Output Structure

```
output/b0b31038-58d0-4c9a-a397-0cae492c15ed/
├── hover_report.md          (this report)
├── screenshots/             (before/after images)
│   └── *.png
├── scenarios/               (individual Gherkin files)
│   └── *.feature
└── behaviors/               (hover detection data)
    └── *.json
```
