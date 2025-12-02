import os
import pytest
from playwright.sync_api import sync_playwright

# Base host for the application under test. Page objects will append paths
# (for example, '/login') as needed so tests can reuse `BASE_URL` consistently.
BASE_URL = "https://captive.encoreskydev.com"


@pytest.fixture(scope="function")
def page():
    """Playwright page fixture.

    Headless is enabled by default to avoid opening a headed browser during CI
    or automated runs. Set environment variable `HEADLESS=false` to run in a
    visible browser when needed.
    """
    if os.getenv("CI") == "true":
        headless = True
    else:
        headless_env = os.getenv("HEADLESS", "true").lower()
        headless = False if headless_env in ("0", "false", "no") else True

    # Allow slowing down Playwright actions for visual debugging
    # e.g. `SLOW_MO=100` will wait 100ms between actions.
    slow_mo = 0
    try:
        slow_mo = int(os.getenv("SLOW_MO", "0"))
    except Exception:
        slow_mo = 0

    # Allow choosing browser: chromium, firefox or webkit
    browser_name = os.getenv("BROWSER", "chromium").lower()

    with sync_playwright() as p:
        if browser_name == "firefox":
            browser = p.firefox.launch(headless=headless, slow_mo=slow_mo)
        elif browser_name == "webkit":
            browser = p.webkit.launch(headless=headless, slow_mo=slow_mo)
        else:
            browser = p.chromium.launch(headless=headless, slow_mo=slow_mo)
        # Allow navigation to sites with self-signed / invalid certs in test env
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        yield page
        context.close()
        browser.close()