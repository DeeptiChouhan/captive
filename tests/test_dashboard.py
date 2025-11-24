import pytest
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage

@pytest.mark.dashboard
def test_dashboard_elements_visibility(page):
    # Step 1: Navigate to login page
    # Navigate to login via the page object (LoginPage.login will navigate)

    # Step 2: Login
    login = LoginPage(page)
    login.login()

    # Step 3: Initialize dashboard page
    dashboard = DashboardPage(page)

    # Step 4: Validate Dashboard loaded
    dashboard.verify_dashboard_loaded()

    # Step 5: Validate User Stats Section
    dashboard.verify_user_stats_section()

    # Step 6: Validate Job Stats Section
    dashboard.verify_job_stats_section()

    # Step 7: Validate Device Stats Section
    dashboard.verify_device_stats_section()
