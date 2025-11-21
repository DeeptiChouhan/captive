import re
import pytest
from playwright.sync_api import Page, expect
from tests.conftest import BASE_URL


@pytest.mark.smoke
def test_valid_login(page: Page):
    # Use configured BASE_URL for navigation instead of a placeholder domain
    page.goto(BASE_URL)

    # Email input
    email_input = page.get_by_placeholder("Email")
    password_input = page.get_by_placeholder("Password")
    login_button = page.get_by_role("button", name="Login")

    # Enter credentials (example valid creds from test data)
    email_input.fill("super.admin@icon.lu")
    password_input.fill("Test@123")

    # Submit
    login_button.click()

    # Assertion → dashboard loaded (use regex instead of lambda)
    expect(page).to_have_url(re.compile("dashboard", re.IGNORECASE))
