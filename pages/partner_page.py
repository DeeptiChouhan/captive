from playwright.sync_api import Page

class PartnerPage:
    def __init__(self, page: Page):
        self.page = page
        self.users_menu = page.get_by_text("Users Management")
        self.partners_menu = page.get_by_text("Partners", exact=True)
        self.add_button = page.locator("a[href='/users/partners/create']")

        self.first_name = page.get_by_placeholder("First Name")
        self.middle_name = page.get_by_placeholder("Middle Name")
        self.last_name = page.get_by_placeholder("Last Name")
        self.email_input = page.get_by_placeholder("Email")
        self.username_input = page.get_by_placeholder("User Name")

        self.gender_dropdown = page.locator("#mui-component-select-gender")
        self.gender_option_female = page.get_by_role("option", name="Female")

        self.save_button = page.get_by_role("button", name="Save")

    def open_add_partner_page(self):
        self.users_menu.click()
        self.partners_menu.click()
        self.add_button.click()

    def fill_partner_form(self, data):
        self.first_name.fill(data["firstName"])
        self.middle_name.fill(data["middleName"])
        self.last_name.fill(data["lastName"])
        self.email_input.fill(data["email"])
        self.username_input.fill(data["userName"])

        self.gender_dropdown.click()
        self.gender_option_female.click()

    def submit_partner_form(self):
        self.save_button.click()
        self.page.wait_for_timeout(2000)
        return True
