import re
import json 
import pytest
from playwright.sync_api import Page, expect
from tests.conftest import BASE_URL

def load_test_data():
    with open("data/user_login.json") as f:
        data= json.load(f)
    invalid_creds=data["invalid_logins"]
    return data, invalid_creds

data, invalid_creds = load_test_data()

@pytest.mark.smoke
def test_valid_login(page: Page):
    # Use configured BASE_URL for navigation instead of a placeholder domain
    page.goto(BASE_URL)

    # Email input
    email_input = page.get_by_placeholder("Email")
    password_input = page.get_by_placeholder("Password")
    login_button = page.get_by_role("button", name="Login")

    # Enter credentials (example valid creds from test data)
    
    email_input.fill(data["superAdmin"]["email"])
    password_input.fill(data["superAdmin"]["password"])

    # Submit
    login_button.click()

    # Assertion → dashboard loaded (use regex instead of lambda)
    expect(page).to_have_url(re.compile("dashboard", re.IGNORECASE))
