"""
Unit tests for browser session management.
Tests the core BrowserManager functionality.
"""

import pytest
import pytest_asyncio
from src.browser import BrowserManager, BrowserSession


class TestBrowserSession:
    """Tests for BrowserSession dataclass."""

    def test_initial_state_is_inactive(self):
        """New session should be inactive."""
        session = BrowserSession()
        assert session.is_active() is False

    def test_session_without_page_is_inactive(self):
        """Session without page should be inactive."""
        session = BrowserSession()
        session.playwright = "mock"
        session.browser = "mock"
        assert session.is_active() is False


class TestBrowserManager:
    """Tests for BrowserManager class."""

    @pytest_asyncio.fixture
    async def manager(self):
        """Create a browser manager for testing."""
        mgr = BrowserManager(headless=True)
        yield mgr
        await mgr.close()

    @pytest.mark.asyncio
    async def test_get_page_creates_session(self, manager):
        """get_page should create a browser session."""
        page = await manager.get_page()
        assert page is not None
        assert manager._session.is_active() is True

    @pytest.mark.asyncio
    async def test_session_persists_across_calls(self, manager):
        """Same page should be returned on multiple calls."""
        page1 = await manager.get_page()
        page2 = await manager.get_page()
        assert page1 is page2

    @pytest.mark.asyncio
    async def test_navigate_returns_title(self, manager):
        """navigate should return page title."""
        title = await manager.navigate("https://example.com")
        assert "Example" in title

    @pytest.mark.asyncio
    async def test_close_cleans_up_session(self, manager):
        """close should cleanup all resources."""
        await manager.get_page()
        assert manager._session.is_active() is True

        await manager.close()
        assert manager._session.is_active() is False
        assert manager._session.page is None


class TestHoverDetection:
    """Tests for hover detection functionality."""

    @pytest_asyncio.fixture
    async def manager_with_page(self):
        """Create manager with a loaded page."""
        mgr = BrowserManager(headless=True)
        await mgr.navigate("https://playwright.dev")
        yield mgr
        await mgr.close()

    @pytest.mark.asyncio
    async def test_find_hoverable_elements_returns_list(self, manager_with_page):
        """find_hoverable_elements should return a list."""
        elements = await manager_with_page.find_hoverable_elements()
        assert isinstance(elements, list)
        assert len(elements) > 0

    @pytest.mark.asyncio
    async def test_hoverable_elements_have_required_fields(self, manager_with_page):
        """Each element should have tag, text, selector."""
        elements = await manager_with_page.find_hoverable_elements()
        for elem in elements[:5]:
            assert "tag" in elem
            assert "selector" in elem

    @pytest.mark.asyncio
    async def test_hover_and_detect_returns_dict(self, manager_with_page):
        """hover_and_detect should return result dict."""
        result = await manager_with_page.hover_and_detect('text="Docs"')
        assert isinstance(result, dict)
        assert "behavior" in result
        assert "selector" in result

    @pytest.mark.asyncio
    async def test_hover_invalid_selector_returns_error(self, manager_with_page):
        """Invalid selector should return error behavior."""
        result = await manager_with_page.hover_and_detect("#nonexistent-element-12345")
        assert result["behavior"] == "error"
        assert "error" in result
