from playwright.sync_api import Page
from datetime import datetime, timedelta
from playwright.sync_api import Page, expect

class JobPage:

    def __init__(self, page: Page):
        self.page = page
        self.job_list = page.get_by_text("Job List")
        self.partners_menu = page.get_by_text("Partners", exact=True)
        self.add_button = page.locator('a[href="/jobs/create"]')
        self.job_type_new_install = "input[type='radio'][value='New Installation']"
        self.job_type_install_change = "input[type='radio'][value='Installation Change']"
        self.change_reason_dropdown = "#mui-component-select-changeReason"
        self.change_reason_option = lambda reason: f"li:has-text('{reason}')"
        self.order_number = "input[name='orderNumber']"
        self.technician_dropdown = "#mui-component-select-assignedTo"
        self.technician_option = lambda tech: f"li:has-text('{tech}')"
        self.schedule_input = "input[name='scheduledDate']"
        self.customer_dropdown = "#mui-component-select-customer"
        self.customer_option = lambda customer: f"li:has-text('{customer}')"
        self.subsidiary_dropdown = "#mui-component-select-subsidiary"
        self.subsidiary_option = lambda subs: f"li:has-text('{subs}')"
        self.contact_dropdown = "#mui-component-select-contactPerson"
        self.address_dropdown = "#mui-component-select-address"
        self.address_option = lambda address: f"li:has-text('{address}')"
        self.device_checkbox = "input[type='checkbox']"
        self.device_option_checkbox = lambda index: f"(//input[@type='checkbox'])[{index}]"
        self.vehicle_license = lambda index: f"input[name='vehicleDetails.{index}.licensePlate']"
        self.vehicle_vin = lambda index: f"input[name='vehicleDetails.{index}.vinNumber']"
        self.vehicle_brand = lambda index: f"input[name='vehicleDetails.{index}.vehicleBrand']"
        self.vehicle_type = lambda index: f"input[name='vehicleDetails.{index}.vehicleType']"
        self.add_vehicle_btn = "button.MuiButton-outlinedPrimary.mui-x2zeaj"
        self.save_btn = "button:has-text('Save')"
        self.toaster = "text=Job Created"
    
    def add_job(self):
        self.job_list.click()
        self.add_button.click()

    def select_new_install_job_type(self):
        self.page.check(self.job_type_new_install)

    def select_install_change_job_type(self):
        self.page.check(self.job_type_install_change)

    def select_change_reason(self, reason):
        self.page.click(self.change_reason_dropdown)
        self.page.click(self.change_reason_option(reason))


    def fill_order_number(self, number):
        self.page.fill(self.order_number, number)

    def select_technician(self, technician):
        self.page.click(self.technician_dropdown)
        self.page.click(self.technician_option(technician))

    def schedule_one_hour_later(self):
        current_time = datetime.now()
        future = current_time + timedelta(hours=1)
        formatted_time = future.strftime("%m/%d/%Y %I:%M %p")
        self.page.fill(self.schedule_input, formatted_time)
        return formatted_time  # return value to match later

    def select_customer(self, customer):
        self.page.click(self.customer_dropdown)
        self.page.click(self.customer_option(customer))

    def select_subsidiary(self, subsidiary):
        self.page.click(self.subsidiary_dropdown)
        self.page.click(self.subsidiary_option(subsidiary))

    def verify_contact_person_options(self, expected_list):
        self.page.click(self.contact_dropdown)

        for item in expected_list:
            expect(self.page.locator("li")).to_contain_text(item)

        # Select the first (usually customer)
        self.page.click(f"li:has-text('{expected_list[0]}')")

    def select_address(self, address):
        self.page.click(self.address_dropdown)
        self.page.click(self.address_option(address))

    def select_device_type(self,option_number):
        self.page.check(self.device_option_checkbox(option_number))

    def fill_vehicle(self, index, license_plate, vin, brand, vtype):
        self.page.fill(self.vehicle_license(index), license_plate)
        self.page.fill(self.vehicle_vin(index), vin)
        self.page.fill(self.vehicle_brand(index), brand)
        self.page.fill(self.vehicle_type(index), vtype)

    def add_new_vehicle(self):
        self.page.click(self.add_vehicle_btn)

    def save_job(self):
        self.page.click(self.save_btn)

    def validate_job_created(self):
        expect(self.page.locator(self.toaster)).to_be_visible()
