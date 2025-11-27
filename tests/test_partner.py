import json
import os
from pages.login_page import LoginPage
from pages.partner_page import PartnerPage
from utils.helpers import delete_user_if_exists
from pages.password_setup import open_invitation_and_set_password


def test_create_partner_and_set_password(page):
    """Create an partner user and set their password via Gmail invitation link."""

    # Step 1: Load partner template from users.json
    with open("data/users.json") as f:
        data = json.load(f)

    partner_data = data["new_partner"]
    dynamic_email = partner_data["email"]

    # Cleanup: delete user if exists
    try:
        delete_user_if_exists(dynamic_email)
    except Exception as e:
        print(f"DEBUG: delete_user_if_exists failed: {e}")

    # Step 3: Login as Super Admin
    login = LoginPage(page)
    login.goto()
    print("DEBUG: Login page loaded:", page.url)
    login.login_with_role("superAdmin")

    # Step 4: Create Admin
    admin_page = PartnerPage(page)
    admin_page.open_add_partner_page()
    admin_page.fill_partner_form(partner_data)
    success = admin_page.submit_partner_form()

    if not success:
        print(f"DEBUG: partner creation failed. Current URL: {page.url}")
        raise AssertionError("Failed to create partner via UI")
    
    print("DEBUG: Partner created successfully via UI:", partner_data["email"])
    # Step 5: Activate Partner via invitation link
    open_invitation_and_set_password(
    page=page,
    
    email=partner_data["email"],
    password=partner_data["password"]
)


    print("Partner created & password set successfully →", partner_data["email"])
