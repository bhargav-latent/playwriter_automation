"""
Unit tests for LangChain tools.
Tests tool functions work correctly with browser.
"""

import pytest
import json
import shutil
from pathlib import Path
from src.tools import generate_gherkin, generate_report
from src.browser import close_browser


class TestGenerateGherkin:
    """Tests for Gherkin generation (sync function, no browser needed)."""

    def test_generates_feature_header(self):
        """Should generate proper feature header."""
        result = generate_gherkin.invoke("[]")
        assert "Feature: Hover Interactions" in result
        assert "Background:" in result

    def test_generates_dropdown_scenario(self):
        """Should generate scenario for dropdown behavior."""
        behaviors = [{
            "element_description": "About Menu",
            "selector": "#about",
            "behavior": "dropdown",
            "revealed_links": [
                {"text": "Team", "href": "/team"},
                {"text": "Contact", "href": "/contact"}
            ]
        }]
        result = generate_gherkin.invoke(json.dumps(behaviors))

        assert "About Menu" in result
        assert "@dropdown" in result
        assert "dropdown menu should become visible" in result
        assert "Team" in result
        assert "/team" in result

    def test_generates_no_change_scenario(self):
        """Should generate scenario for no-change behavior."""
        behaviors = [{
            "element_description": "Static Button",
            "selector": "#btn",
            "behavior": "no_change",
            "revealed_links": []
        }]
        result = generate_gherkin.invoke(json.dumps(behaviors))

        assert "Static Button" in result
        assert "@no-effect" in result
        assert "no dropdown menu should appear" in result

    def test_handles_empty_behaviors(self):
        """Should handle empty behavior list."""
        result = generate_gherkin.invoke("[]")
        assert "Feature:" in result
        # Should still have header but no scenarios

    def test_handles_invalid_json(self):
        """Should handle invalid JSON gracefully."""
        result = generate_gherkin.invoke("not valid json")
        assert "Feature:" in result  # Should still return header

    def test_limits_links_in_output(self):
        """Should limit number of links shown."""
        behaviors = [{
            "element_description": "Big Menu",
            "selector": "#menu",
            "behavior": "dropdown",
            "revealed_links": [
                {"text": f"Link {i}", "href": f"/link{i}"}
                for i in range(20)
            ]
        }]
        result = generate_gherkin.invoke(json.dumps(behaviors))

        # Should only show first 5 links
        assert "Link 0" in result
        assert "Link 4" in result
        assert "Link 10" not in result


class TestGenerateReport:
    """Tests for report generation (sync function, no browser needed)."""

    @pytest.fixture(autouse=True)
    def cleanup_output(self):
        """Cleanup output directory after each test."""
        yield
        output_dir = Path("output")
        if output_dir.exists():
            shutil.rmtree(output_dir)

    def test_generates_report_file(self):
        """Should create a markdown report file."""
        behaviors = [{
            "element_description": "Test Menu",
            "selector": "#test",
            "behavior": "dropdown",
            "revealed_links": [{"text": "Link1", "href": "/link1"}],
            "screenshot_before": "output/screenshots/001_test_before.png",
            "screenshot_after": "output/screenshots/002_test_after.png"
        }]
        gherkin = "Feature: Test\n  Scenario: Test scenario"

        result = generate_report.invoke({
            "behaviors_json": json.dumps(behaviors),
            "gherkin_content": gherkin,
            "report_title": "Test Report"
        })

        assert "hover_report.md" in result
        report_path = Path(result)
        assert report_path.exists()

    def test_report_contains_gherkin(self):
        """Should include Gherkin content in report."""
        gherkin = "Feature: Hover Test\n  Scenario: Click button"
        result = generate_report.invoke({
            "behaviors_json": "[]",
            "gherkin_content": gherkin,
            "report_title": "Test Report"
        })

        report_content = Path(result).read_text()
        assert "Feature: Hover Test" in report_content
        assert "Gherkin Test Scenarios" in report_content

    def test_report_contains_screenshot_table(self):
        """Should include before/after screenshot table."""
        behaviors = [{
            "element_description": "Nav Menu",
            "selector": "#nav",
            "behavior": "dropdown",
            "revealed_links": [],
            "screenshot_before": "output/screenshots/001_nav_before.png",
            "screenshot_after": "output/screenshots/002_nav_after.png"
        }]

        result = generate_report.invoke({
            "behaviors_json": json.dumps(behaviors),
            "gherkin_content": "Feature: Test",
            "report_title": "Screenshot Test"
        })

        report_content = Path(result).read_text()
        assert "| Before Hover | After Hover |" in report_content
        assert "Nav Menu" in report_content
        assert "dropdown" in report_content

    def test_report_summary_counts(self):
        """Should include summary with counts."""
        behaviors = [
            {"behavior": "dropdown", "element_description": "A"},
            {"behavior": "dropdown", "element_description": "B"},
            {"behavior": "no_change", "element_description": "C"},
            {"behavior": "error", "element_description": "D"},
        ]

        result = generate_report.invoke({
            "behaviors_json": json.dumps(behaviors),
            "gherkin_content": "Feature: Test",
            "report_title": "Summary Test"
        })

        report_content = Path(result).read_text()
        assert "Total elements tested:** 4" in report_content
        assert "Dropdowns detected:** 2" in report_content
        assert "No change:** 1" in report_content
        assert "Errors:** 1" in report_content

    def test_handles_empty_behaviors(self):
        """Should handle empty behaviors list."""
        result = generate_report.invoke({
            "behaviors_json": "[]",
            "gherkin_content": "Feature: Empty",
            "report_title": "Empty Test"
        })

        report_path = Path(result)
        assert report_path.exists()
        content = report_path.read_text()
        assert "Total elements tested:** 0" in content


class TestToolIntegration:
    """Integration tests that require browser."""

    @pytest.fixture(autouse=True)
    async def cleanup(self):
        """Cleanup browser after each test."""
        yield
        await close_browser()

    @pytest.mark.asyncio
    async def test_navigate_tool(self):
        """navigate_to_url tool should work."""
        from src.tools import navigate_to_url

        result = await navigate_to_url.ainvoke("https://example.com")
        assert "Navigated to" in result
        assert "Example" in result

    @pytest.mark.asyncio
    async def test_find_elements_tool(self):
        """find_hoverable_elements tool should return JSON."""
        from src.tools import navigate_to_url, find_hoverable_elements

        await navigate_to_url.ainvoke("https://example.com")
        result = await find_hoverable_elements.ainvoke({})

        # Should be valid JSON
        elements = json.loads(result)
        assert isinstance(elements, list)

    @pytest.mark.asyncio
    async def test_hover_tool(self):
        """hover_element tool should detect behavior."""
        from src.tools import navigate_to_url, hover_element

        await navigate_to_url.ainvoke("https://playwright.dev")
        result = await hover_element.ainvoke({
            "selector": 'text="Docs"',
            "description": "Docs navigation link"
        })

        # Should be valid JSON
        data = json.loads(result)
        assert "behavior" in data
        assert "element_description" in data


class TestEndToEndWorkflow:
    """End-to-end workflow test."""

    @pytest.fixture(autouse=True)
    async def cleanup(self):
        """Cleanup browser after each test."""
        yield
        await close_browser()

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete workflow: navigate -> find -> hover -> generate."""
        from src.tools import navigate_to_url, find_hoverable_elements, hover_element, generate_gherkin

        # 1. Navigate
        nav_result = await navigate_to_url.ainvoke("https://playwright.dev")
        assert "Playwright" in nav_result

        # 2. Find elements
        elements_json = await find_hoverable_elements.ainvoke({})
        elements = json.loads(elements_json)
        assert len(elements) > 0

        # 3. Hover on first element with text
        test_element = None
        for elem in elements:
            if elem.get("text") and len(elem["text"]) > 0:
                test_element = elem
                break

        behaviors = []
        if test_element:
            hover_result = await hover_element.ainvoke({
                "selector": test_element["selector"],
                "description": test_element["text"]
            })
            behaviors.append(json.loads(hover_result))

        # 4. Generate Gherkin
        gherkin = generate_gherkin.invoke(json.dumps(behaviors))
        assert "Feature:" in gherkin
        assert "Scenario:" in gherkin
