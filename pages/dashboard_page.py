from playwright.sync_api import Page, expect

class DashboardPage:
    def __init__(self, page: Page):
        self.page = page

        # Page title
        self.dashboard_title = "span.MuiTypography-body1:text('Dashboard')"

        # User Stats Section
        self.user_stats_header = "h5.MuiTypography-h5:text('User Stats')"
        self.total_admins = "span.MuiTypography-overline:text('Total Admins')"
        self.total_partners = "span.MuiTypography-overline:text('Total Partners')"
        self.total_customers = "span.MuiTypography-overline:text('Total Customers')"
        self.total_subsidiaries = "span.MuiTypography-overline:text('Total Subsidiaries')"
        self.total_roles = "span.MuiTypography-overline:text('Total Roles')"
        self.total_technicians = "span.MuiTypography-overline:text('Total Technicians')"

        # Job Stats Section
        self.job_stats_header = "h5.MuiTypography-h5:text('Job Stats')"
        self.total_jobs = "span.MuiTypography-overline:text('Total Jobs')"
        self.draft_jobs = "span.MuiTypography-overline:text('Draft Jobs')"
        self.assigned_jobs = "span.MuiTypography-overline:text('Assigned Jobs')"
        self.arrived_jobs = "span.MuiTypography-overline:text('Arrived Jobs')"
        self.started_jobs = "span.MuiTypography-overline:text('Started Jobs')"
        self.completed_jobs = "span.MuiTypography-overline:text('Completed Jobs')"

        # Device Stats
        self.device_stats_header = "h5.MuiTypography-h5:text('Device Stats')"
        self.total_routers = "span.MuiTypography-overline:text('Total Routers')"
        # Use XPath with normalize-space to match the exact text and avoid
        # substring collisions (e.g. 'Unassigned Routers' contains 'Assigned Routers').
        self.assigned_routers = "xpath=//span[normalize-space(text())='Assigned Routers']"
        self.unassigned_routers = "xpath=//span[normalize-space(text())='Unassigned Routers']"

    def verify_dashboard_loaded(self):
        expect(self.page.locator(self.dashboard_title)).to_be_visible()

    def verify_user_stats_section(self):
        expect(self.page.locator(self.user_stats_header)).to_be_visible()
        expect(self.page.locator(self.total_admins)).to_be_visible()
        expect(self.page.locator(self.total_partners)).to_be_visible()
        expect(self.page.locator(self.total_customers)).to_be_visible()
        expect(self.page.locator(self.total_subsidiaries)).to_be_visible()
        expect(self.page.locator(self.total_roles)).to_be_visible()
        expect(self.page.locator(self.total_technicians)).to_be_visible()

    def verify_job_stats_section(self):
        expect(self.page.locator(self.job_stats_header)).to_be_visible()
        expect(self.page.locator(self.total_jobs)).to_be_visible()
        expect(self.page.locator(self.draft_jobs)).to_be_visible()
        expect(self.page.locator(self.assigned_jobs)).to_be_visible()
        expect(self.page.locator(self.arrived_jobs)).to_be_visible()
        expect(self.page.locator(self.started_jobs)).to_be_visible()
        expect(self.page.locator(self.completed_jobs)).to_be_visible()

    def verify_device_stats_section(self):
        expect(self.page.locator(self.device_stats_header)).to_be_visible()
        expect(self.page.locator(self.total_routers)).to_be_visible()
        expect(self.page.locator(self.assigned_routers)).to_be_visible()
        expect(self.page.locator(self.unassigned_routers)).to_be_visible()
