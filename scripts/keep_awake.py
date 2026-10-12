"""Visit the deployed app in a real browser so Streamlit Community Cloud keeps it awake.

Community Cloud puts an app to sleep after 12 hours without visitors. A plain
HTTP request does not count as a visit, and a sleeping app shows a wake-up
button that has to be clicked, so this opens the page in headless Chromium.

Usage: python scripts/keep_awake.py https://<your-app>.streamlit.app
"""

import sys
import time

from playwright.sync_api import Error, sync_playwright

WAKE_BUTTON = "Yes, get this app back up!"
APP_READY = ".brand-name"  # drawn by ui.header(), so the app script has really run
TIMEOUT_S = 240            # a sleeping app can take a few minutes to boot


def find(page, locate):
    """First match across all frames: Community Cloud runs the app inside an iframe."""
    for frame in page.frames:
        try:
            target = locate(frame)
            if target.count():
                return target.first
        except Error:  # frame went away while the page was redirecting
            continue
    return None


def main(url: str) -> int:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)

        woken = False
        deadline = time.monotonic() + TIMEOUT_S
        while time.monotonic() < deadline:
            if find(page, lambda frame: frame.locator(APP_READY)):
                page.wait_for_timeout(5000)  # hold the session open so it registers as a visit
                print("App was asleep and is running again." if woken else "App is awake.")
                return 0
            button = None if woken else find(page, lambda frame: frame.get_by_role("button", name=WAKE_BUTTON))
            if button:
                button.click()
                woken = True
                print("App was asleep. Waking it up...")
            page.wait_for_timeout(2000)

        print(f"App did not load within {TIMEOUT_S}s (last page: {page.url}).", file=sys.stderr)
        return 1


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].startswith("http"):
        sys.exit("Usage: python scripts/keep_awake.py https://<your-app>.streamlit.app")
    sys.exit(main(sys.argv[1]))
