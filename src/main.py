"""
Main entry point for Hover Detection Agent POC.

Usage:
    python -m src.main --url "https://example.com"
    python -m src.main --url "https://example.com" --output output/tests.feature
"""

import asyncio
import argparse
import json
from pathlib import Path
from datetime import datetime

from .browser import BrowserManager, close_browser
from .tools import generate_gherkin


async def detect_hover_behaviors(url: str, headless: bool = False) -> list:
    """
    Detect all hover behaviors on a page.

    Args:
        url: URL to analyze
        headless: Run browser in headless mode

    Returns:
        List of detected behaviors
    """
    manager = BrowserManager(headless=headless)
    behaviors = []

    try:
        print(f"\n[1/4] Navigating to {url}...")
        title = await manager.navigate(url)
        print(f"      Page title: {title}")

        print("\n[2/4] Finding hoverable elements...")
        elements = await manager.find_hoverable_elements()
        print(f"      Found {len(elements)} hoverable elements")

        print("\n[3/4] Testing hover behaviors...")
        # Test each element (limit to 15 for POC)
        for i, elem in enumerate(elements[:15]):
            selector = elem.get("selector", "")
            text = elem.get("text", "unknown")[:30]

            if not selector:
                continue

            print(f"      [{i+1}/{min(len(elements), 15)}] Hovering: {text}...")
            result = await manager.hover_and_detect(selector)
            result["element_description"] = text if text else elem.get("tag", "element")

            behaviors.append(result)

            # Log if dropdown found
            if result["behavior"] == "dropdown":
                links = result.get("revealed_links", [])
                print(f"            -> DROPDOWN detected with {len(links)} links")

        print(f"\n[4/4] Analysis complete!")
        print(f"      Total elements tested: {len(behaviors)}")
        print(f"      Dropdowns found: {sum(1 for b in behaviors if b['behavior'] == 'dropdown')}")

    finally:
        await manager.close()

    return behaviors


def save_gherkin(gherkin: str, output_path: str) -> None:
    """Save Gherkin content to file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(gherkin)
    print(f"\n      Saved to: {path}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Detect hover behaviors and generate Gherkin tests"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="URL to analyze"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path for Gherkin (default: output/<domain>_<timestamp>.feature)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("HOVER DETECTION AGENT - POC")
    print("=" * 60)

    # Detect behaviors
    behaviors = await detect_hover_behaviors(args.url, args.headless)

    # Generate Gherkin
    print("\n[+] Generating Gherkin scenarios...")
    gherkin = generate_gherkin.invoke(json.dumps(behaviors))

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        from urllib.parse import urlparse
        domain = urlparse(args.url).netloc.replace(".", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"output/{domain}_{timestamp}.feature"

    # Save
    save_gherkin(gherkin, output_path)

    # Print summary
    print("\n" + "=" * 60)
    print("GENERATED GHERKIN:")
    print("=" * 60)
    print(gherkin)

    return behaviors, gherkin


if __name__ == "__main__":
    asyncio.run(main())
