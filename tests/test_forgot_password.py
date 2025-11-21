from pages.login_page import LoginPage
from pages.forgot_password_page import ForgotPasswordPage
from tests.conftest import BASE_URL

def test_forgot_password_redirect(page):
    login = LoginPage(page)
    login.goto(BASE_URL)
    login.click_forgot_password()
    # Expect to land on forgot page path
    assert "password/forgot" in page.url or "forgot" in page.url

def test_forgot_password_blank_email(page):
    login = LoginPage(page)
    login.goto(BASE_URL)
    login.click_forgot_password()
    fp = ForgotPasswordPage(page)
    fp.enter_email("")
    fp.click_send_link()
    assert "Email is required" in fp.get_visible_errors()

def test_forgot_password_invalid_unregistered(page):
    login = LoginPage(page)
    login.goto(BASE_URL)
    login.click_forgot_password()
    fp = ForgotPasswordPage(page)
    fp.enter_email("nouser@test.com")
    fp.click_send_link()
    # either user not found or some message - assert presence
    errors = fp.get_visible_errors()
    assert any(e for e in errors if "User not found.." in e or "not found" in e)