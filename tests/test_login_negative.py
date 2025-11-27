import json
from pages.login_page import LoginPage

def load_test_data():
    with open("data/user_login.json") as f:
        data= json.load(f)
    invalid_creds=data["invalid_logins"]
    return data, invalid_creds

data, invalid_creds = load_test_data()

def test_blank_email(page):
    login = LoginPage(page)
    login.goto()
    login.enter_email(invalid_creds["blank_email"])
    login.enter_password("ValidPassword123")
    login.click_login()
    assert login.get_error_message() == "Email is required"

def test_invalid_email_format(page):
    login = LoginPage(page)
    login.goto()
    login.enter_email(invalid_creds["invalid_email_format"])
    login.enter_password("ValidPassword123")
    login.click_login()
    assert login.get_error_message() == "Invalid email"

def test_unregistered_email(page):
    login = LoginPage(page)
    login.goto()
    login.enter_email(invalid_creds["unregistered_email"])
    login.enter_password("ValidPassword123")
    login.click_login()
    assert login.get_error_message() == "User not found.."

def test_wrong_password(page):
    login = LoginPage(page)
    login.goto()
    login.enter_email("super.admin@icon.lu")
    login.enter_password(invalid_creds["wrong_password"])
    login.click_login()
    assert login.get_error_message() == "The password provided does not meet requirements.."
