import json
import os
from pages.login_page import LoginPage
from pages.admin_page import AdminPage
from utils.helpers import delete_user_if_exists
from pages.password_setup import open_invitation_and_set_password


def test_create_admin_and_set_password(page):
    """Create an admin user and set their password via Gmail invitation link."""

    # Step 1: Load admin template from users.json
    with open("data/users.json") as f:
        data = json.load(f)

    admin_data = data["new_admin"]
    gmail_user = data["gmail"]["username"]
    gmail_pass = data["gmail"]["app_password"]

    # Step 2: Make email and username dynamic
    # (Keeps +1a but ensures uniqueness)
    dynamic_email = "deepti.chouhan+1a@encoresky.com"

    # Cleanup: delete user if exists
    try:
        delete_user_if_exists(dynamic_email)
    except Exception as e:
        print(f"DEBUG: delete_user_if_exists failed: {e}")

    # Apply dynamic email & username
    admin_data["email"] = dynamic_email
    admin_data["userName"] = "deepti_chouhan_1a"

    # Step 3: Login as Super Admin
    login = LoginPage(page)
    login.goto()
    print("DEBUG: Login page loaded:", page.url)
    login.login_with_role("superAdmin")

    # Step 4: Create Admin
    admin_page = AdminPage(page)
    admin_page.open_add_admin_page()
    admin_page.fill_admin_form(admin_data)
    success = admin_page.submit_admin_form()

    if not success:
        print(f"DEBUG: Admin creation failed. Current URL: {page.url}")
        raise AssertionError("Failed to create admin via UI")
    
    print("DEBUG: Admin created successfully via UI:", admin_data["email"])
    # Step 5: Activate Admin via invitation link
    open_invitation_and_set_password(
    page=page,
    email=admin_data["email"],
    new_password="test@123"
)


    print("Admin created & password set successfully →", admin_data["email"])
