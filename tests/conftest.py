import os
import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "https://captive.encoreskydev.com/login"


@pytest.fixture(scope="function")
def page():
    """Playwright page fixture.

    Headless is enabled by default to avoid opening a headed browser during CI
    or automated runs. Set environment variable `HEADLESS=false` to run in a
    visible browser when needed.
    """
    headless_env = os.getenv("HEADLESS", "false").lower()
    headless = False if headless_env in ("0", "false", "no") else False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        # Allow navigation to sites with self-signed / invalid certs in test env
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        yield page
        context.close()
        browser.close()