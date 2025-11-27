import json
import os
from pages.login_page import LoginPage
from pages.technician import TechnicianPage
from utils.helpers import delete_user_if_exists
from pages.password_setup import open_invitation_and_set_password


def test_create_technician_and_set_password(page):
    """Create an technician user and set their password via Gmail invitation link."""

    # Step 1: Load technician template from users.json
    with open("data/users.json") as f:
        data = json.load(f)

    technician_data = data["new_technician"]
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
    technician_data["email"] = dynamic_email
    technician_data["userName"] = "deepti_chouhan_1a"

    # Step 3: Login as Super Admin
    login = LoginPage(page)
    login.goto()
    print("DEBUG: Login page loaded:", page.url)
    login.login_with_role("superAdmin")

    # Step 4: Create Technicians
    technician_page = TechnicianPage(page)
    technician_page.open_add_technicians_page()
    technician_page.fill_technicians_form(technician_data)
    success = technician_page.submit_technician_form()

    if not success:
        print(f"DEBUG: Technicians creation failed. Current URL: {page.url}")
        raise AssertionError("Failed to create technicians via UI")
    
    print("DEBUG: Technicians created successfully via UI:", technician_data["email"])
    # Step 5: Activate Technicians via invitation link
    open_invitation_and_set_password(
    page=page,
    email=technician_data["email"],
    new_password="test@123"
)


    print("Technicians created & password set successfully →", technician_data["email"])
