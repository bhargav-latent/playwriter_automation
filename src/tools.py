"""
Custom LangChain tools for hover detection.
These tools use the persistent BrowserManager session.

Uses synchronous tools to avoid event loop conflicts with LangGraph server on Windows.
"""

import json
import logging
import asyncio
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
from langchain_core.tools import tool

_logger = logging.getLogger("tools")

# Global session ID for organizing output by thread
_current_session_id: Optional[str] = None


def set_session_id(session_id: str) -> None:
    """Set the current session ID for organizing output folders."""
    global _current_session_id
    _current_session_id = session_id
    _logger.info(f"Session ID set to: {session_id}")


def get_session_id() -> Optional[str]:
    """Get the current session ID."""
    return _current_session_id

# Thread pool for running async browser operations
_browser_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="browser_tool")


def _run_async_in_thread_sync(coro):
    """Run an async coroutine in a separate thread with ProactorEventLoop on Windows (sync version)."""
    import sys

    def run():
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    future = _browser_executor.submit(run)
    return future.result()


async def _run_async_in_thread(coro):
    """Run an async coroutine in a separate thread with ProactorEventLoop on Windows (async version)."""
    import sys

    def run():
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    return await asyncio.to_thread(run)


@tool
async def navigate_to_url(url: str) -> str:
    """
    Navigate to a URL and return page info.

    Args:
        url: The URL to navigate to

    Returns:
        String with navigation result and page title
    """
    _logger.info(f"navigate_to_url called with url={url}")

    async def _navigate():
        from .browser import get_browser_manager
        session_id = get_session_id()
        manager = await get_browser_manager(session_id=session_id)
        title = await manager.navigate(url)
        return title

    try:
        title = await _run_async_in_thread(_navigate())
        _logger.info(f"Navigation successful, title={title}")
        return f"Navigated to {url}. Page title: {title}"
    except Exception as e:
        _logger.error(f"navigate_to_url failed: {type(e).__name__}: {e}")
        raise


@tool
async def get_page_structure() -> str:
    """
    Get comprehensive page structure using accessibility tree.
    Call this AFTER navigation to understand the page layout before testing hovers.

    Returns:
        JSON with page structure including:
        - summary: counts of menus, buttons, links, hover candidates
        - menus: menu-related elements (menubar, menuitem, etc.)
        - buttons: all buttons on the page
        - links: navigation links
        - hover_candidates: elements likely to have hover behavior (aria-haspopup, cursor:pointer, etc.)
        - landmarks: page regions (navigation, banner, main, etc.)
    """
    async def _get_structure():
        from .browser import get_browser_manager
        session_id = get_session_id()
        manager = await get_browser_manager(session_id=session_id)
        return await manager.get_page_structure()

    structure = await _run_async_in_thread(_get_structure())
    return json.dumps(structure, indent=2)


@tool
async def find_hoverable_elements() -> str:
    """
    Find all potentially hoverable elements on the current page using CSS selectors.
    Note: For better coverage, use get_page_structure() first to understand the page.

    Returns:
        JSON string of hoverable elements with selectors
    """
    async def _find():
        from .browser import get_browser_manager
        session_id = get_session_id()
        manager = await get_browser_manager(session_id=session_id)
        return await manager.find_hoverable_elements()

    elements = await _run_async_in_thread(_find())
    return json.dumps(elements, indent=2)


@tool
async def save_gherkin_scenario(element_name: str, gherkin_content: str) -> str:
    """
    Save an individual Gherkin scenario file for a hover interaction.
    Call this AFTER hover_element to save a custom Gherkin scenario based on the detected behavior.

    Args:
        element_name: Name of the element (used for filename, e.g., "Products Menu")
        gherkin_content: The complete Gherkin feature content to save

    Returns:
        Path to the saved .feature file
    """
    async def _save():
        from .browser import get_browser_manager
        session_id = get_session_id()
        manager = await get_browser_manager(session_id=session_id)
        return manager.save_scenario_file(element_name, gherkin_content)

    filepath = await _run_async_in_thread(_save())
    return f"Saved Gherkin scenario to: {filepath}"


@tool
async def hover_element(selector: str, description: str, capture_screenshots: bool = True, force: bool = False) -> str:
    """
    Hover over an element and detect what changes. Captures before/after screenshots by default.
    Automatically saves behavior data to disk for report generation.

    IMPORTANT: After calling this tool, you MUST call save_gherkin_scenario with a Gherkin
    feature file that describes the detected behavior.

    Args:
        selector: CSS selector or text selector for the element
        description: Human-readable description of the element
        capture_screenshots: Whether to capture before/after screenshots (default: True)
        force: If True, force the hover even if another element intercepts it (default: False).
               Use this when normal hover fails with "intercepts pointer events" error.

    Returns:
        JSON string with detected behavior and screenshot paths
    """
    async def _hover():
        from .browser import get_browser_manager
        session_id = get_session_id()
        manager = await get_browser_manager(session_id=session_id)
        return await manager.hover_and_detect(selector, element_name=description, capture_screenshots=capture_screenshots, force=force)

    async def _save_behavior(behavior_data: dict):
        from .browser import get_browser_manager
        session_id = get_session_id()
        manager = await get_browser_manager(session_id=session_id)
        return manager.save_behavior_file(description, behavior_data)

    result = await _run_async_in_thread(_hover())
    result["element_description"] = description

    # Automatically save behavior to disk for report generation
    behavior_file = await _run_async_in_thread(_save_behavior(result))
    result["behavior_file"] = behavior_file
    _logger.info(f"Saved behavior to: {behavior_file}")

    return json.dumps(result, indent=2)


@tool
async def generate_gherkin(behaviors_json: str) -> str:
    """
    Generate Gherkin test scenarios from detected hover behaviors.

    Args:
        behaviors_json: JSON string array of detected behaviors

    Returns:
        Gherkin feature file content
    """
    try:
        behaviors = json.loads(behaviors_json)
    except json.JSONDecodeError:
        behaviors = []

    gherkin = """Feature: Hover Interactions
  As a user visiting the website
  I want hover interactions to reveal navigation content
  So that I can access additional pages and information

  Background:
    Given I am on the target page
    And any popup dialogs have been dismissed

"""

    dropdown_scenarios = []
    no_change_scenarios = []

    for behavior in behaviors:
        desc = behavior.get("element_description", "element")
        selector = behavior.get("selector", "")
        behavior_type = behavior.get("behavior", "unknown")
        links = behavior.get("revealed_links", [])

        if behavior_type == "dropdown":
            scenario = f"""
  @hover @dropdown
  Scenario: {desc} reveals dropdown menu on hover
    When I hover over "{desc}"
    Then a dropdown menu should become visible
    And the dropdown should contain {len(links)} link(s)"""

            if links:
                scenario += "\n    And I should see the following links:"
                scenario += "\n      | Link Text | URL |"
                for link in links[:5]:
                    text = link.get("text", "N/A")[:30]
                    href = link.get("href", "N/A")
                    scenario += f"\n      | {text} | {href} |"

            scenario += f"""
    And each link should be clickable
"""
            dropdown_scenarios.append(scenario)

        elif behavior_type in ("no_change", "style_change", "unreachable"):
            no_change_scenarios.append(f"""
  @hover @no-effect
  Scenario: {desc} has no hover dropdown
    When I hover over "{desc}"
    Then no dropdown menu should appear
    And the element should respond to click only
""")

    # Add dropdown scenarios first
    for scenario in dropdown_scenarios:
        gherkin += scenario

    # Add a few no-change scenarios (not all, to keep it lean)
    for scenario in no_change_scenarios[:3]:
        gherkin += scenario

    return gherkin


@tool
async def generate_tldr(website_name: str = "website") -> str:
    """
    Generate a TLDR (executive summary) of the hover detection results.
    Call this BEFORE generate_report to create a high-level summary.

    Reads all behavior data from disk and produces a concise summary including:
    - Total elements tested
    - Key findings (dropdowns, tooltips, errors)
    - Actionable insights
    - Test coverage assessment

    Args:
        website_name: Name of the website being tested (for the summary title)

    Returns:
        TLDR summary text that should be passed to generate_report
    """
    from datetime import datetime

    # Determine output directory based on session_id
    session_id = get_session_id()
    base_output = Path("output")
    if session_id:
        output_dir = base_output / session_id
    else:
        output_dir = base_output

    behaviors_dir = output_dir / "behaviors"
    scenarios_dir = output_dir / "scenarios"

    # Load behaviors from disk
    behaviors = []
    if behaviors_dir.exists():
        behavior_files = sorted(behaviors_dir.glob("*.json"))
        for bf in behavior_files:
            try:
                behavior_data = json.loads(bf.read_text(encoding="utf-8"))
                behaviors.append(behavior_data)
            except (json.JSONDecodeError, IOError) as e:
                _logger.warning(f"Failed to load behavior file {bf}: {e}")

    # Count scenario files
    scenario_count = len(list(scenarios_dir.glob("*.feature"))) if scenarios_dir.exists() else 0

    # Calculate statistics
    total_elements = len(behaviors)
    dropdown_count = sum(1 for b in behaviors if b.get('behavior') == 'dropdown')
    tooltip_count = sum(1 for b in behaviors if b.get('behavior') == 'tooltip')
    content_count = sum(1 for b in behaviors if b.get('behavior') == 'content_revealed')
    no_change_count = sum(1 for b in behaviors if b.get('behavior') == 'no_change')
    unreachable_count = sum(1 for b in behaviors if b.get('behavior') == 'unreachable')

    # Calculate success metrics (unreachable elements are expected in dynamic sites, not failures)
    successful_interactions = dropdown_count + tooltip_count + content_count + no_change_count
    success_rate = (successful_interactions / total_elements * 100) if total_elements > 0 else 0
    interactive_elements = dropdown_count + tooltip_count + content_count

    # Collect dropdown details
    dropdown_details = []
    for b in behaviors:
        if b.get('behavior') == 'dropdown':
            desc = b.get('element_description', b.get('selector', 'Unknown'))
            links = b.get('revealed_links', [])
            dropdown_details.append(f"  - **{desc}**: reveals {len(links)} links")

    # Collect unreachable element details (first 3)
    unreachable_details = []
    for b in behaviors:
        if b.get('behavior') == 'unreachable':
            desc = b.get('element_description', b.get('selector', 'Unknown'))
            unreachable_details.append(f"  - {desc}")

    # Build TLDR
    tldr = f"""## TLDR - Executive Summary

**Website:** {website_name}
**Test Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Session ID:** `{session_id or 'N/A'}`

### At a Glance

| Metric | Value |
|--------|-------|
| Total Elements Tested | {total_elements} |
| Interactive Elements Found | {interactive_elements} |
| Test Success Rate | {success_rate:.1f}% |
| Gherkin Scenarios Generated | {scenario_count} |

### Key Findings

"""

    # Dropdowns
    if dropdown_count > 0:
        tldr += f"**✅ Dropdowns Detected ({dropdown_count}):**\n"
        for detail in dropdown_details[:5]:
            tldr += f"{detail}\n"
        tldr += "\n"
    else:
        tldr += "**ℹ️ No dropdown menus detected**\n\n"

    # Tooltips
    if tooltip_count > 0:
        tldr += f"**✅ Tooltips Detected ({tooltip_count})**\n\n"

    # Content revealed
    if content_count > 0:
        tldr += f"**✅ Content Revealed on Hover ({content_count}):** Elements that show additional content on hover\n\n"

    # Static elements
    if no_change_count > 0:
        tldr += f"**ℹ️ Static Elements ({no_change_count}):** Elements with no hover behavior (click-only)\n\n"

    # Unreachable elements
    if unreachable_count > 0:
        tldr += f"**ℹ️ Unreachable Elements ({unreachable_count}):** Elements that could not be hovered (out of viewport, hidden, or dynamically loaded)\n"
        for detail in unreachable_details[:3]:
            tldr += f"{detail}\n"
        if len(unreachable_details) > 3:
            tldr += f"  - ... and {len(unreachable_details) - 3} more\n"
        tldr += "\n"

    # Insights
    tldr += """### Insights

"""

    if interactive_elements > 0:
        tldr += f"- The site has **{interactive_elements} interactive hover elements** that enhance user navigation\n"

    if dropdown_count > 0:
        total_links = sum(len(b.get('revealed_links', [])) for b in behaviors if b.get('behavior') == 'dropdown')
        tldr += f"- Dropdown menus reveal a total of **{total_links} navigation links**\n"

    if unreachable_count > 0:
        tldr += f"- **{unreachable_count} elements** were unreachable (out of viewport, hidden, or dynamically loaded - this is expected for modern dynamic websites)\n"

    if success_rate >= 80:
        tldr += "- **Good test coverage** - most elements were successfully tested\n"
    elif success_rate >= 50:
        tldr += "- **Moderate test coverage** - some elements had interaction issues\n"
    else:
        tldr += "- **Limited test coverage** - many elements could not be tested; consider manual verification\n"

    tldr += "\n---\n\n"

    # Save TLDR to disk for generate_report to use
    tldr_path = output_dir / "tldr.md"
    tldr_path.write_text(tldr, encoding="utf-8")
    _logger.info(f"TLDR saved to: {tldr_path}")

    return tldr


@tool
async def generate_report(report_title: str = "Hover Detection Report", tldr_content: str = "") -> str:
    """
    Generate a markdown report combining individual Gherkin scenarios with before/after screenshot comparisons.
    Automatically reads behavior data and TLDR from disk if available.

    IMPORTANT: Call generate_tldr BEFORE this tool to create the executive summary.

    Args:
        report_title: Title for the report (default: "Hover Detection Report")
        tldr_content: TLDR summary from generate_tldr (optional, falls back to disk file)

    Returns:
        Path to the generated markdown report file
    """
    from datetime import datetime

    # Determine output directory based on session_id
    session_id = get_session_id()
    base_output = Path("output")
    if session_id:
        output_dir = base_output / session_id
    else:
        output_dir = base_output

    output_dir.mkdir(parents=True, exist_ok=True)
    scenarios_dir = output_dir / "scenarios"
    behaviors_dir = output_dir / "behaviors"

    # Try to load TLDR from disk if not provided
    if not tldr_content:
        tldr_path = output_dir / "tldr.md"
        if tldr_path.exists():
            tldr_content = tldr_path.read_text(encoding="utf-8")
            _logger.info(f"Loaded TLDR from: {tldr_path}")

    # Try to load behaviors from disk first (more reliable than LLM-passed parameter)
    behaviors = []
    if behaviors_dir.exists():
        behavior_files = sorted(behaviors_dir.glob("*.json"))
        for bf in behavior_files:
            try:
                behavior_data = json.loads(bf.read_text(encoding="utf-8"))
                behaviors.append(behavior_data)
                _logger.info(f"Loaded behavior from: {bf}")
            except (json.JSONDecodeError, IOError) as e:
                _logger.warning(f"Failed to load behavior file {bf}: {e}")

    # Build a map of behaviors by element description for fuzzy matching
    # Also index by scenario_file if available
    behavior_by_scenario = {}
    behavior_by_description = {}

    for behavior in behaviors:
        # Index by scenario_file if available
        scenario_file = behavior.get("scenario_file")
        if scenario_file:
            scenario_name = Path(scenario_file).name
            behavior_by_scenario[scenario_name] = behavior

        # Index by element_description for fuzzy matching
        desc = behavior.get("element_description", "").lower()
        if desc:
            behavior_by_description[desc] = behavior

    def find_matching_behavior(scenario_stem: str) -> dict:
        """Find behavior that matches the scenario file stem using fuzzy matching."""
        # First try exact scenario_file match
        scenario_filename = scenario_stem + ".feature"
        if scenario_filename in behavior_by_scenario:
            return behavior_by_scenario[scenario_filename]

        # Fuzzy match: extract key words from scenario name and match against descriptions
        # e.g., "Company_Menu" -> ["company", "menu"]
        keywords = [w.lower() for w in scenario_stem.split("_") if len(w) > 1]

        best_match = None
        best_score = 0

        for desc, behavior in behavior_by_description.items():
            # Count how many keywords appear in the description
            score = sum(1 for kw in keywords if kw in desc)
            if score > best_score:
                best_score = score
                best_match = behavior

        # Require at least half the keywords to match
        if best_match and best_score >= len(keywords) / 2:
            return best_match

        return {}

    # Build markdown content
    report = f"""# {report_title}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Session ID: `{session_id or 'N/A'}`

---

"""

    # Add TLDR at the top if available
    if tldr_content:
        report += tldr_content
    else:
        report += """## TLDR - Executive Summary

*No TLDR summary available. Run generate_tldr before generate_report for an executive summary.*

---

"""

    report += """## Table of Contents

1. [TLDR - Executive Summary](#tldr---executive-summary)
2. [Test Scenarios with Evidence](#test-scenarios-with-evidence)
3. [Summary](#summary)

---

## Test Scenarios with Evidence

Each scenario includes the Gherkin specification followed by before/after screenshot comparison.

"""

    # Read all individual scenario files from the scenarios directory
    scenario_files = []
    if scenarios_dir.exists():
        scenario_files = sorted(scenarios_dir.glob("*.feature"))

    has_screenshots = False

    # Interactive behaviors that should be included in detailed report
    interactive_behaviors = {"dropdown", "tooltip", "content_revealed"}

    if scenario_files:
        for scenario_file in scenario_files:
            scenario_name = scenario_file.stem.replace("_", " ")
            scenario_content = scenario_file.read_text(encoding="utf-8")

            # Find matching behavior for this scenario using fuzzy matching
            behavior = find_matching_behavior(scenario_file.stem)
            behavior_type = behavior.get("behavior", "unknown")

            # Skip no_change and unreachable scenarios - they only appear in TLDR
            if behavior_type in ("no_change", "unreachable"):
                continue

            screenshot_before = behavior.get("screenshot_before")
            screenshot_after = behavior.get("screenshot_after")
            revealed_links = behavior.get("revealed_links", [])

            report += f"""### {scenario_name}

**Behavior Detected:** `{behavior_type}`
**Scenario File:** `scenarios/{scenario_file.name}`

```gherkin
{scenario_content}
```

"""
            # Add screenshots immediately after the Gherkin
            if screenshot_before or screenshot_after:
                has_screenshots = True
                report += "#### Screenshot Evidence\n\n"

                if screenshot_before and screenshot_after:
                    before_path = Path(screenshot_before)
                    after_path = Path(screenshot_after)
                    before_rel = f"screenshots/{before_path.name}"
                    after_rel = f"screenshots/{after_path.name}"

                    report += f"""| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before]({before_rel}) | ![After]({after_rel}) |

"""
                elif screenshot_before:
                    before_path = Path(screenshot_before)
                    before_rel = f"screenshots/{before_path.name}"
                    report += f"**Screenshot:** ![Before]({before_rel})\n\n"

            # Add revealed links if any
            if revealed_links:
                report += "#### Revealed Links\n\n"
                for link in revealed_links[:5]:
                    text = link.get("text", "N/A")
                    href = link.get("href", "N/A")
                    report += f"- [{text}]({href})\n"
                report += "\n"

            report += "---\n\n"
    else:
        # Fallback to combined gherkin content if no individual files
        report += f"""### Combined Scenarios

```gherkin
{gherkin_content}
```

---

"""

    # Add any INTERACTIVE behaviors that didn't have matching scenario files
    # Filter out no_change and error - they only appear in TLDR
    unmatched_behaviors = [
        b for b in behaviors
        if not b.get("scenario_file") and b.get("behavior") in interactive_behaviors
    ]
    if unmatched_behaviors:
        report += """## Additional Interactive Elements

These interactive hover elements were detected but don't have individual scenario files.

"""
        for behavior in unmatched_behaviors:
            desc = behavior.get("element_description", behavior.get("selector", "Unknown element"))
            behavior_type = behavior.get("behavior", "unknown")
            screenshot_before = behavior.get("screenshot_before")
            screenshot_after = behavior.get("screenshot_after")
            revealed_links = behavior.get("revealed_links", [])

            report += f"""### {desc}

**Behavior:** `{behavior_type}`

"""
            if screenshot_before or screenshot_after:
                has_screenshots = True
                if screenshot_before and screenshot_after:
                    before_path = Path(screenshot_before)
                    after_path = Path(screenshot_after)
                    before_rel = f"screenshots/{before_path.name}"
                    after_rel = f"screenshots/{after_path.name}"

                    report += f"""| Before Hover | After Hover |
|:------------:|:-----------:|
| ![Before]({before_rel}) | ![After]({after_rel}) |

"""
            # Add revealed links if any
            if revealed_links:
                report += "#### Revealed Links\n\n"
                for link in revealed_links[:5]:
                    text = link.get("text", "N/A")
                    href = link.get("href", "N/A")
                    report += f"- [{text}]({href})\n"
                report += "\n"

            report += "---\n\n"

    if not has_screenshots and not scenario_files:
        report += "*No screenshots were captured during this test run.*\n\n"

    # Add summary section
    dropdown_count = sum(1 for b in behaviors if b.get('behavior') == 'dropdown')
    tooltip_count = sum(1 for b in behaviors if b.get('behavior') == 'tooltip')
    content_count = sum(1 for b in behaviors if b.get('behavior') == 'content_revealed')
    no_change_count = sum(1 for b in behaviors if b.get('behavior') == 'no_change')
    unreachable_count = sum(1 for b in behaviors if b.get('behavior') == 'unreachable')

    report += f"""## Summary

| Metric | Count |
|--------|-------|
| Total elements tested | {len(behaviors)} |
| Dropdowns detected | {dropdown_count} |
| Tooltips detected | {tooltip_count} |
| Content revealed | {content_count} |
| No change | {no_change_count} |
| Unreachable | {unreachable_count} |
| Scenario files generated | {len(scenario_files)} |

### Output Structure

```
output/{session_id or ''}/
├── hover_report.md          (this report)
├── screenshots/             (before/after images)
│   └── *.png
├── scenarios/               (individual Gherkin files)
│   └── *.feature
└── behaviors/               (hover detection data)
    └── *.json
```
"""

    # Write report
    report_path = output_dir / "hover_report.md"
    report_path.write_text(report, encoding="utf-8")

    return str(report_path)


def get_all_tools() -> List:
    """Return all available tools."""
    return [
        navigate_to_url,
        get_page_structure,
        find_hoverable_elements,
        hover_element,
        save_gherkin_scenario,
        generate_gherkin,
        generate_tldr,
        generate_report,
    ]
