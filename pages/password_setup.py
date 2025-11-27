from utils.email_utils import get_invitation_link
from pages.login_page import LoginPage

def open_invitation_and_set_password(page, email, password):
    print(f"Fetching invitation link for: {email}")
    
    page.wait_for_timeout(20000)

    # Get latest link from Gmail API
    link = get_invitation_link(email)
    print("Invitation link:", link)

    # Use the same Playwright page
    page.goto(link)

    pw_fields = page.locator("input[type='password']")
    pw_fields.nth(0).fill(password)
    pw_fields.nth(1).fill(password)

    page.get_by_role("button", name="Submit").click()
    print("Password successfully set!")
