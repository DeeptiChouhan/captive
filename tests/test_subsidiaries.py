import json
import os
from pages.login_page import LoginPage
from pages.subsidiaries import SubsidiariesPage
from utils.helpers import delete_user_if_exists
from pages.password_setup import open_invitation_and_set_password


def test_create_subsidiaries_and_set_password(page):
    """Create an subsidiaries user and set their password via Gmail invitation link."""

    # Step 1: Load subsidiaries template from users.json
    with open("data/users.json") as f:
        data = json.load(f)

    subsidiaries_data = data["new_subsidiaries"]
    dynamic_email = subsidiaries_data["email"]

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

    # Step 4: Create Subsidiaries
    subsidiaries_page = SubsidiariesPage(page)
    subsidiaries_page.open_add_subsidiaries_page()
    subsidiaries_page.fill_subsidiaries_form(subsidiaries_data)
    success = subsidiaries_page.submit_subsidiaries_form()

    if not success:
        print(f"DEBUG: Subsidiaries creation failed. Current URL: {page.url}")
        raise AssertionError("Failed to create subsidiaries via UI")
    
    print("DEBUG: Subsidiaries created successfully via UI:", subsidiaries_data["email"])
    # Step 5: Activate Subsidiaries via invitation link
    open_invitation_and_set_password(
    page=page,
    email=subsidiaries_data["email"],
    password=subsidiaries_data["password"]
)


    print("Subsidiaries created & password set successfully →", subsidiaries_data["email"])
