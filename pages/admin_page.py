import json
from playwright.sync_api import Page

class AdminPage:

    def __init__(self, page: Page):
        self.page = page

        # Top Navigation → Users → Admins
        # Prefer exact link selectors to avoid matching multiple elements that
        # contain the word 'Admins' (e.g., headings, cards, totals).
        self.users_menu = page.get_by_text("Users Management")
        # Use the first occurrence (likely the navigation link) to avoid
        # collisions with other anchors on the page that reuse the same href.
        self.admins_button = page.locator("a[href='/users/admins']").first

        # Add Admin Button
        self.add_admin_button = page.locator("a[href='/users/admins/create']")

        # Form Fields
        self.first_name = page.get_by_placeholder("First Name")
        self.middle_name = page.get_by_placeholder("Middle Name")
        self.last_name = page.get_by_placeholder("Last Name")
        self.email_input = page.get_by_placeholder("Email")
        self.username_input = page.get_by_placeholder("User Name")

        # Gender dropdown
        self.gender_dropdown = page.locator("#mui-component-select-gender")
        self.gender_option = lambda gender: page.get_by_role("option", name=gender)

        # Save button
        self.save_btn = page.get_by_role("button", name="Save")

    # Navigate to Admins → Add Admin
    def open_add_admin_page(self):
        self.users_menu.click()
        self.admins_button.click()
        self.add_admin_button.click()

    # Fill admin form using JSON
    def fill_admin_form(self, data: dict):
        self.first_name.fill(data["firstName"])
        self.middle_name.fill(data["middleName"])
        self.last_name.fill(data["lastName"])
        self.email_input.fill(data["email"])
        self.username_input.fill(data["userName"])

        # Select gender
        self.gender_dropdown.click()
        self.gender_option(data["gender"]).click()

    def submit_admin_form(self):
        self.save_btn.click()
        # Wait for either a success toast (sonner toaster) or a navigation
        # back to the admins listing. Return True if we detect success.
        try:
            # Wait for a toaster container used by the app's sonner notifications
            self.page.wait_for_selector('[data-sonner-toaster]', timeout=7000)
            # Read toaster text and check for success keywords
            try:
                toaster = self.page.locator('[data-sonner-toaster]')
                text = toaster.first.text_content() or ""
                if text and 'admin' in text.lower() and ('created' in text.lower() or 'success' in text.lower()):
                    return True
            except Exception:
                pass
        except Exception:
            pass

        try:
            self.page.wait_for_url('**/users/admins', timeout=7000)
            return True
        except Exception:
            return False
