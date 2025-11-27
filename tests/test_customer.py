import json
import os
from pages.login_page import LoginPage
from pages.customer_page import CustomerPage
from utils.helpers import delete_user_if_exists
from pages.password_setup import open_invitation_and_set_password

def test_create_customer_and_set_password(page):
    """Create a customer user and set their password via Gmail invitation link."""

    # Step 1: Load customer template from users.json
    with open("data/users.json") as f:
        data = json.load(f)

    customer_data = data["new_customer"]

    # Cleanup: delete user if exists
    try:
        delete_user_if_exists(customer_data["email"])
    except Exception as e:
        print(f"DEBUG: delete_user_if_exists failed: {e}")

    # Step 3: Login as Super Admin
    login = LoginPage(page)
    login.goto()
    print("DEBUG: Login page loaded:", page.url)
    login.login_with_role("superAdmin")

    # Step 4: Create Admin
    admin_page = CustomerPage(page)
    admin_page.open_add_customer_page()
    admin_page.fill_customer_form(customer_data)
    success = admin_page.submit_customer_form()

    if not success:
        print(f"DEBUG: Admin creation failed. Current URL: {page.url}")
        raise AssertionError("Failed to create admin via UI")
    
    print("DEBUG: Customer created successfully via UI:", customer_data["email"])
    # Step 5: Activate Customer via invitation link
    open_invitation_and_set_password(
    page=page,
    email=customer_data["email"],
    password=customer_data["password"]
)
    print("Customer created & password set successfully →", customer_data["email"])
