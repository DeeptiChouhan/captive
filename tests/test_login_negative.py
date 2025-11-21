import json
from pages.login_page import LoginPage

def load_test_data():
    with open("data/login_invalid.json") as f:
        return json.load(f)

data = load_test_data()

def test_blank_email(page):
    login = LoginPage(page)
    login.goto()
    login.enter_email(data["blank_email"])
    login.enter_password("ValidPassword123")
    login.click_login()
    assert login.get_error_message() == "Email is required"

def test_invalid_email_format(page):
    login = LoginPage(page)
    login.goto()
    login.enter_email(data["invalid_email_format"])
    login.enter_password("ValidPassword123")
    login.click_login()
    assert login.get_error_message() == "Invalid email"

def test_unregistered_email(page):
    login = LoginPage(page)
    login.goto()
    login.enter_email(data["unregistered_email"])
    login.enter_password("ValidPassword123")
    login.click_login()
    assert login.get_error_message() == "User not found.."

def test_wrong_password(page):
    login = LoginPage(page)
    login.goto()
    login.enter_email("super.admin@icon.lu")
    login.enter_password(data["wrong_password"])
    login.click_login()
    assert login.get_error_message() == "The password provided does not meet requirements.."
