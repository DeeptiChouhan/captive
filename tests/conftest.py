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
    headless_env = os.getenv("HEADLESS", "true").lower()
    # Default to headless unless explicitly disabled by setting HEADLESS to
    # 'false', '0', or 'no'. This makes CI and local runs consistent.
    headless = False if headless_env in ("0", "false", "no") else True

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        # Allow navigation to sites with self-signed / invalid certs in test env
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        yield page
        context.close()
        browser.close()