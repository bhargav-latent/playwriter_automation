"""
Browser session management for Playwright.
Maintains a single persistent browser session across all tool calls.

Uses synchronous Playwright API internally to avoid event loop conflicts
with LangGraph server on Windows (which uses SelectorEventLoop).
"""

import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
_logger = logging.getLogger("browser")

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, Playwright


@dataclass
class BrowserSession:
    """Holds browser session state."""
    playwright: Optional[Playwright] = None
    browser: Optional[Browser] = None
    context: Optional[BrowserContext] = None
    page: Optional[Page] = None

    def is_active(self) -> bool:
        """Check if session is active."""
        return self.page is not None and not self.page.is_closed()


class BrowserManager:
    """
    Manages a single persistent Playwright browser session.

    Uses synchronous Playwright API internally, wrapped for async access.
    This avoids event loop conflicts with LangGraph server on Windows.

    Usage:
        manager = BrowserManager(session_id="my-session")
        page = await manager.get_page()
        await manager.navigate("https://example.com")
        await manager.close()
    """

    def __init__(self, headless: bool = False, output_dir: str = "output", session_id: str = None):
        self.headless = headless
        self._session = BrowserSession()
        self.session_id = session_id

        # Organize output by session_id if provided
        base_output = Path(output_dir)
        if session_id:
            self.output_dir = base_output / session_id
        else:
            self.output_dir = base_output

        self.screenshots_dir = self.output_dir / "screenshots"
        self.scenarios_dir = self.output_dir / "scenarios"
        self.behaviors_dir = self.output_dir / "behaviors"
        self._screenshot_counter = 0
        self._behavior_counter = 0

    def _create_session_sync(self) -> None:
        """Create a new browser session (sync, runs in thread)."""
        _logger.info(f"_create_session_sync called, platform={sys.platform}")

        # CRITICAL: Clear the running loop reference to avoid Playwright's async detection
        # Playwright checks asyncio._get_running_loop() and throws an error if it finds one
        try:
            # This removes the running loop from this thread's context
            asyncio.set_event_loop(None)
        except Exception:
            pass

        _logger.info("Starting sync_playwright")
        self._session.playwright = sync_playwright().start()
        _logger.info("sync_playwright started successfully")
        self._session.browser = self._session.playwright.chromium.launch(
            headless=self.headless
        )
        self._session.context = self._session.browser.new_context()
        self._session.page = self._session.context.new_page()

    def _close_sync(self) -> None:
        """Close browser and cleanup resources (sync, runs in thread)."""
        if self._session.browser:
            self._session.browser.close()
        if self._session.playwright:
            self._session.playwright.stop()
        self._session = BrowserSession()

    async def get_page(self) -> Page:
        """Get the current page, creating browser if needed."""
        if not self._session.is_active():
            await asyncio.to_thread(self._create_session_sync)
        return self._session.page

    async def close(self) -> None:
        """Close browser and cleanup resources."""
        await asyncio.to_thread(self._close_sync)

    def _navigate_sync(self, url: str) -> str:
        """Navigate to URL (sync, runs in thread)."""
        self._session.page.goto(url, wait_until="networkidle")
        return self._session.page.title()

    async def navigate(self, url: str) -> str:
        """Navigate to URL and return page title."""
        await self.get_page()  # Ensure session exists
        return await asyncio.to_thread(self._navigate_sync, url)

    def _take_screenshot_sync(self, name: str, full_page: bool = False) -> str:
        """Take screenshot (sync, runs in thread)."""
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        self._screenshot_counter += 1
        filename = f"{self._screenshot_counter:03d}_{safe_name}.png"
        filepath = self.screenshots_dir / filename
        self._session.page.screenshot(path=str(filepath), full_page=full_page)
        return str(filepath)

    async def take_screenshot(self, name: str, full_page: bool = False) -> str:
        """
        Take a screenshot and save to output directory.

        Args:
            name: Base name for the screenshot file (will be sanitized)
            full_page: Whether to capture the full scrollable page

        Returns:
            Path to the saved screenshot file
        """
        await self.get_page()  # Ensure session exists
        return await asyncio.to_thread(self._take_screenshot_sync, name, full_page)

    def save_scenario_file(self, element_name: str, gherkin_content: str) -> str:
        """
        Save an individual Gherkin scenario file.

        Args:
            element_name: Name of the element (used for filename)
            gherkin_content: Gherkin scenario content

        Returns:
            Path to the saved scenario file
        """
        self.scenarios_dir.mkdir(parents=True, exist_ok=True)
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in element_name)[:50]
        filename = f"{safe_name}.feature"
        filepath = self.scenarios_dir / filename
        filepath.write_text(gherkin_content, encoding="utf-8")
        return str(filepath)

    def save_behavior_file(self, element_name: str, behavior_data: dict) -> str:
        """
        Save hover behavior data to a JSON file for report generation.

        Args:
            element_name: Name of the element (used for filename)
            behavior_data: Dictionary containing hover detection results

        Returns:
            Path to the saved behavior JSON file
        """
        import json
        self.behaviors_dir.mkdir(parents=True, exist_ok=True)
        self._behavior_counter += 1
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in element_name)[:50]
        filename = f"{self._behavior_counter:03d}_{safe_name}.json"
        filepath = self.behaviors_dir / filename
        filepath.write_text(json.dumps(behavior_data, indent=2), encoding="utf-8")
        return str(filepath)

    def _get_snapshot_sync(self) -> dict:
        """Get accessibility snapshot (sync, runs in thread)."""
        return self._session.page.accessibility.snapshot()

    async def get_snapshot(self) -> dict:
        """Get accessibility snapshot of current page."""
        await self.get_page()
        return await asyncio.to_thread(self._get_snapshot_sync)

    def _get_page_structure_sync(self) -> dict:
        """Get page structure (sync, runs in thread)."""
        page = self._session.page

        # Get all interactive elements using JavaScript with ARIA and accessibility info
        structure = page.evaluate("""
            () => {
                const menus = [];
                const buttons = [];
                const links = [];
                const hover_candidates = [];
                const landmarks = [];

                // Helper to build selector for an element
                function buildSelector(el) {
                    if (el.id) return '#' + el.id;
                    if (el.getAttribute('data-testid')) return `[data-testid="${el.getAttribute('data-testid')}"]`;

                    const text = (el.innerText || el.getAttribute('aria-label') || '').trim();
                    if (text && text.length < 30 && text.length > 0) {
                        return `text="${text}"`;
                    }

                    // Fallback to tag + class
                    let selector = el.tagName.toLowerCase();
                    if (el.className && typeof el.className === 'string') {
                        const mainClass = el.className.split(' ')[0];
                        if (mainClass) selector += '.' + mainClass;
                    }
                    return selector;
                }

                // Find elements by ARIA roles
                const roleSelectors = {
                    menus: ['[role="menubar"]', '[role="menu"]', '[role="menuitem"]', '[role="menuitemcheckbox"]', '[role="menuitemradio"]'],
                    buttons: ['[role="button"]', 'button'],
                    links: ['[role="link"]', 'a[href]'],
                    landmarks: ['[role="navigation"]', '[role="banner"]', '[role="main"]', '[role="complementary"]', 'nav', 'header', 'main', 'aside']
                };

                // Collect menu elements
                roleSelectors.menus.forEach(sel => {
                    document.querySelectorAll(sel).forEach(el => {
                        const rect = el.getBoundingClientRect();
                        if (rect.width === 0 || rect.height === 0) return;

                        menus.push({
                            role: el.getAttribute('role') || el.tagName.toLowerCase(),
                            name: (el.innerText || el.getAttribute('aria-label') || '').trim().substring(0, 50),
                            selector: buildSelector(el),
                            hasPopup: el.getAttribute('aria-haspopup'),
                            expanded: el.getAttribute('aria-expanded'),
                        });
                    });
                });

                // Collect buttons
                roleSelectors.buttons.forEach(sel => {
                    document.querySelectorAll(sel).forEach(el => {
                        const rect = el.getBoundingClientRect();
                        if (rect.width === 0 || rect.height === 0) return;

                        buttons.push({
                            role: 'button',
                            name: (el.innerText || el.getAttribute('aria-label') || '').trim().substring(0, 50),
                            selector: buildSelector(el),
                            hasPopup: el.getAttribute('aria-haspopup'),
                            expanded: el.getAttribute('aria-expanded'),
                        });
                    });
                });

                // Collect links
                roleSelectors.links.forEach(sel => {
                    document.querySelectorAll(sel).forEach(el => {
                        const rect = el.getBoundingClientRect();
                        if (rect.width === 0 || rect.height === 0) return;

                        const text = (el.innerText || el.getAttribute('aria-label') || '').trim();
                        if (!text) return;  // Skip links without text

                        links.push({
                            role: 'link',
                            name: text.substring(0, 50),
                            href: el.getAttribute('href'),
                            selector: buildSelector(el),
                            hasPopup: el.getAttribute('aria-haspopup'),
                        });
                    });
                });

                // Collect landmarks
                roleSelectors.landmarks.forEach(sel => {
                    document.querySelectorAll(sel).forEach(el => {
                        const rect = el.getBoundingClientRect();
                        if (rect.width === 0 || rect.height === 0) return;

                        landmarks.push({
                            role: el.getAttribute('role') || el.tagName.toLowerCase(),
                            name: el.getAttribute('aria-label') || '',
                            selector: buildSelector(el),
                        });
                    });
                });

                // Find hover candidates - elements likely to have hover behavior
                document.querySelectorAll('*').forEach(el => {
                    const style = window.getComputedStyle(el);
                    const rect = el.getBoundingClientRect();

                    if (rect.width === 0 || rect.height === 0) return;
                    if (style.display === 'none' || style.visibility === 'hidden') return;

                    const hasPointerCursor = style.cursor === 'pointer';
                    const hasAriaPopup = el.getAttribute('aria-haspopup');
                    const hasAriaExpanded = el.getAttribute('aria-expanded') !== null;
                    const hasDataToggle = el.getAttribute('data-toggle') || el.getAttribute('data-bs-toggle');
                    const hasDropdownClass = el.className && typeof el.className === 'string' && (
                        el.className.includes('dropdown') ||
                        el.className.includes('menu') ||
                        el.className.includes('nav')
                    );

                    // Only include if it has hover-related attributes
                    if (hasAriaPopup || hasAriaExpanded || hasDataToggle || (hasDropdownClass && hasPointerCursor)) {
                        hover_candidates.push({
                            tag: el.tagName,
                            name: (el.innerText || el.getAttribute('aria-label') || '').trim().substring(0, 50),
                            selector: buildSelector(el),
                            ariaPopup: hasAriaPopup,
                            ariaExpanded: el.getAttribute('aria-expanded'),
                            dataToggle: hasDataToggle || null,
                            role: el.getAttribute('role'),
                        });
                    }
                });

                return { menus, buttons, links, landmarks, hover_candidates };
            }
        """)

        # Deduplicate by selector
        def dedupe(items):
            seen = set()
            result = []
            for item in items:
                key = item.get('selector', '') + item.get('name', '')
                if key not in seen:
                    seen.add(key)
                    result.append(item)
            return result

        menus = dedupe(structure['menus'])
        buttons = dedupe(structure['buttons'])
        links = dedupe(structure['links'])
        landmarks = dedupe(structure['landmarks'])
        hover_candidates = dedupe(structure['hover_candidates'])

        return {
            "page_title": page.title(),
            "url": page.url,
            "summary": {
                "menus": len(menus),
                "buttons": len(buttons),
                "links": len(links),
                "landmarks": len(landmarks),
                "hover_candidates": len(hover_candidates),
            },
            "menus": menus[:20],
            "buttons": buttons[:20],
            "links": links[:30],
            "landmarks": landmarks[:10],
            "hover_candidates": hover_candidates[:30],
        }

    async def get_page_structure(self) -> dict:
        """
        Get comprehensive page structure using ARIA roles and accessibility attributes.
        Returns interactive elements, their roles, and hierarchy.
        """
        await self.get_page()
        return await asyncio.to_thread(self._get_page_structure_sync)

    def _find_hoverable_elements_sync(self) -> list:
        """Find hoverable elements (sync, runs in thread)."""
        page = self._session.page

        return page.evaluate("""
            () => {
                const results = [];
                const seen = new Set();

                document.querySelectorAll('a, button, [role="button"], [role="menuitem"], [class*="dropdown"], [class*="menu"]').forEach((el, idx) => {
                    const style = window.getComputedStyle(el);
                    const rect = el.getBoundingClientRect();

                    // Skip hidden or off-screen elements
                    if (rect.width === 0 || rect.height === 0) return;
                    if (style.display === 'none' || style.visibility === 'hidden') return;

                    const text = (el.innerText || el.getAttribute('aria-label') || '').trim().substring(0, 50);
                    const key = `${el.tagName}-${text}`;

                    // Skip duplicates
                    if (seen.has(key)) return;
                    seen.add(key);

                    // Build a reliable selector
                    let selector = '';
                    if (el.id) {
                        selector = `#${el.id}`;
                    } else if (el.getAttribute('data-testid')) {
                        selector = `[data-testid="${el.getAttribute('data-testid')}"]`;
                    } else if (text && text.length > 0 && text.length < 30) {
                        selector = `text="${text}"`;
                    } else {
                        selector = `${el.tagName.toLowerCase()}:nth-of-type(${idx + 1})`;
                    }

                    results.push({
                        tag: el.tagName,
                        text: text,
                        selector: selector,
                        hasExpandButton: el.querySelector('[class*="expand"], [class*="arrow"], [class*="caret"]') !== null,
                        cursor: style.cursor
                    });
                });

                return results;
            }
        """)

    async def find_hoverable_elements(self) -> list:
        """Find all potentially hoverable elements."""
        await self.get_page()
        return await asyncio.to_thread(self._find_hoverable_elements_sync)

    def _hover_and_detect_sync(self, selector: str, element_name: str, capture_screenshots: bool) -> dict:
        """Hover and detect changes (sync, runs in thread)."""
        page = self._session.page

        # JavaScript to get all visible interactive elements with their positions
        get_visible_elements_js = """
            () => {
                const elements = [];
                const selectors = [
                    'ul', 'li', 'a', 'button',
                    '[class*="dropdown"]', '[class*="menu"]', '[class*="submenu"]',
                    '[class*="popup"]', '[class*="tooltip"]', '[class*="popover"]',
                    '[role="menu"]', '[role="listbox"]', '[role="tooltip"]'
                ];

                document.querySelectorAll(selectors.join(', ')).forEach(el => {
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);

                    // Check if element is visible
                    const isVisible = (
                        rect.width > 0 &&
                        rect.height > 0 &&
                        style.display !== 'none' &&
                        style.visibility !== 'hidden' &&
                        style.opacity !== '0' &&
                        rect.top < window.innerHeight &&
                        rect.bottom > 0
                    );

                    if (isVisible) {
                        elements.push({
                            tag: el.tagName,
                            className: el.className || '',
                            id: el.id || '',
                            text: (el.innerText || '').trim().substring(0, 50),
                            href: el.getAttribute('href') || '',
                            top: Math.round(rect.top),
                            left: Math.round(rect.left),
                            // Create unique key for comparison
                            key: `${el.tagName}-${el.className}-${(el.innerText || '').trim().substring(0, 30)}-${Math.round(rect.top)}-${Math.round(rect.left)}`
                        });
                    }
                });
                return elements;
            }
        """

        # Generate safe name for screenshots
        safe_name = element_name or selector
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in safe_name)[:30]

        screenshot_before = None
        screenshot_after = None

        try:
            # Reset page state before testing hover
            # 1. Move mouse to neutral position (top-left corner)
            page.mouse.move(0, 0)
            page.wait_for_timeout(200)

            # 2. Press Escape to close any open dropdowns/modals
            page.keyboard.press("Escape")
            page.wait_for_timeout(200)

            # 3. Click on body to deselect/close any hover menus
            page.click("body", position={"x": 10, "y": 10}, force=True)
            page.wait_for_timeout(300)

            # 4. Move mouse away again after click
            page.mouse.move(0, 0)
            page.wait_for_timeout(300)

            # Capture BEFORE state
            before_elements = page.evaluate(get_visible_elements_js)
            before_keys = set(el['key'] for el in before_elements)

            # Take BEFORE screenshot
            if capture_screenshots:
                screenshot_before = self._take_screenshot_sync(f"{safe_name}_before")

            # Perform HOVER with scroll into view and retry logic
            hover_success = False
            hover_error = None

            # Try different strategies to hover the element
            strategies = [
                lambda: page.locator(selector).first.scroll_into_view_if_needed(timeout=5000),
                lambda: page.evaluate(f"document.querySelector('{selector.replace(chr(34), chr(92)+chr(34))}')?.scrollIntoView({{block: 'center', behavior: 'instant'}})") if not selector.startswith('text=') else None,
            ]

            # First, try to scroll element into view
            for strategy in strategies:
                if strategy is None:
                    continue
                try:
                    strategy()
                    page.wait_for_timeout(300)
                    break
                except Exception:
                    pass

            # Now try to hover with increased timeout
            try:
                page.hover(selector, timeout=8000)
                hover_success = True
            except Exception as e:
                # Try with locator.first if direct selector fails
                try:
                    page.locator(selector).first.hover(timeout=8000)
                    hover_success = True
                except Exception as e2:
                    hover_error = str(e2)

            if not hover_success:
                return {
                    "selector": selector,
                    "element_name": element_name,
                    "behavior": "unreachable",
                    "error": f"Could not hover element: {hover_error}",
                    "screenshot_before": screenshot_before,
                    "screenshot_after": None,
                }

            page.wait_for_timeout(600)  # Wait for animations/transitions

            # Take AFTER screenshot
            if capture_screenshots:
                screenshot_after = self._take_screenshot_sync(f"{safe_name}_after")

            # Capture AFTER state
            after_elements = page.evaluate(get_visible_elements_js)
            after_keys = set(el['key'] for el in after_elements)

            # Find NEW elements (appeared after hover)
            new_keys = after_keys - before_keys
            new_elements = [el for el in after_elements if el['key'] in new_keys]

            # Filter to get only links from new elements
            revealed_links = [
                {"text": el['text'], "href": el['href']}
                for el in new_elements
                if el['tag'] == 'A' and el['href']
            ]

            # Determine behavior
            behavior = "no_change"
            if len(new_elements) > 0:
                # Check what type of elements appeared
                has_menu_items = any(
                    'menu' in el.get('className', '').lower() or
                    'dropdown' in el.get('className', '').lower() or
                    el['tag'] in ('LI', 'UL')
                    for el in new_elements
                )
                has_tooltip = any(
                    'tooltip' in el.get('className', '').lower() or
                    'popover' in el.get('className', '').lower()
                    for el in new_elements
                )

                if has_menu_items or len(revealed_links) > 0:
                    behavior = "dropdown"
                elif has_tooltip:
                    behavior = "tooltip"
                else:
                    behavior = "content_revealed"

            result = {
                "selector": selector,
                "new_elements_count": len(new_elements),
                "revealed_links": revealed_links[:10],
                "behavior": behavior,
                "new_element_types": list(set(el['tag'] for el in new_elements))[:5]
            }

            if capture_screenshots:
                result["screenshot_before"] = screenshot_before
                result["screenshot_after"] = screenshot_after

            return result

        except Exception as e:
            result = {
                "selector": selector,
                "new_elements_count": 0,
                "revealed_links": [],
                "behavior": "unreachable",
                "error": str(e)
            }

            if capture_screenshots and screenshot_before:
                result["screenshot_before"] = screenshot_before
                result["screenshot_after"] = screenshot_after

            return result

    async def hover_and_detect(self, selector: str, element_name: str = "", capture_screenshots: bool = True) -> dict:
        """
        Hover over element and detect DOM changes.

        Args:
            selector: CSS selector or text selector for the element
            element_name: Human-readable name for screenshot filenames
            capture_screenshots: Whether to capture before/after screenshots

        Returns:
            dict with keys: selector, dom_changed, new_elements, behavior, revealed_links,
                           and optionally screenshot_before, screenshot_after
        """
        await self.get_page()
        return await asyncio.to_thread(
            self._hover_and_detect_sync, selector, element_name, capture_screenshots
        )


# Global instance for simple usage
_manager: Optional[BrowserManager] = None
_current_session_id: Optional[str] = None


async def get_browser_manager(headless: bool = True, session_id: str = None) -> BrowserManager:
    """
    Get or create global browser manager.

    Args:
        headless: Run browser in headless mode (default: True for server environments)
        session_id: Optional session/thread ID for organizing output folders

    Returns:
        BrowserManager instance
    """
    global _manager, _current_session_id

    # If session_id changed, close existing manager and create new one
    if _manager is not None and session_id != _current_session_id:
        await _manager.close()
        _manager = None

    if _manager is None:
        _manager = BrowserManager(headless=headless, session_id=session_id)
        _current_session_id = session_id

    return _manager


async def close_browser() -> None:
    """Close global browser manager."""
    global _manager
    if _manager:
        await _manager.close()
        _manager = None
