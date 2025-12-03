import re
import json 
import pytest
from playwright.sync_api import Page, expect
from tests.conftest import BASE_URL
from pages.login_page import LoginPage

def load_test_data():
    with open("data/user_login.json") as f:
        data= json.load(f)
    invalid_creds=data["invalid_logins"]
    return data, invalid_creds
data, invalid_creds = load_test_data()

@pytest.mark.smoke
def test_valid_login(page: Page):
    page.goto(BASE_URL)
    email_input = page.get_by_placeholder("Email")
    password_input = page.get_by_placeholder("Password")
    login_button = page.get_by_role("button", name="Login")
    email_input.fill(data["superAdmin"]["email"])
    password_input.fill(data["superAdmin"]["password"])
    login_button.click()
    expect(page).to_have_url(re.compile("dashboard", re.IGNORECASE))

@pytest.mark.smoke
def test_blank_email(page):
    login = LoginPage(page)
    login.goto()
    login.enter_email(invalid_creds["blank_email"])
    login.enter_password("ValidPassword123")
    login.click_login()
    assert login.get_error_message() == "Email is required"

@pytest.mark.smoke
def test_invalid_email_format(page):
    login = LoginPage(page)
    login.goto()
    login.enter_email(invalid_creds["invalid_email_format"])
    login.enter_password("ValidPassword123")
    login.click_login()
    assert login.get_error_message() == "Invalid email"

@pytest.mark.smoke
def test_unregistered_email(page):
    login = LoginPage(page)
    login.goto()
    login.enter_email(invalid_creds["unregistered_email"])
    login.enter_password("ValidPassword123")
    login.click_login()
    assert login.get_error_message() == "User not found.."

@pytest.mark.smoke
def test_wrong_password(page):
    login = LoginPage(page)
    login.goto()
    login.enter_email("super.admin@icon.lu")
    login.enter_password(invalid_creds["wrong_password"])
    login.click_login()
    assert login.get_error_message() == "The password provided does not meet requirements.."

