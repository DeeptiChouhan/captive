from playwright.sync_api import Page, expect

class ForgotPasswordPage:
    def __init__(self, page: Page):
        self.page = page
        # Updated selectors from provided HTML snippet with fallbacks
        self.email_input = page.locator('input[placeholder="Enter your email"], input[placeholder="Email"], input[name="email"]')
        # button text may vary; use a flexible locator
        self.send_link_button = page.get_by_role("button", name="Send recovery link")
        if not self.send_link_button:
            self.send_link_button = page.locator('button:has-text("Send")')

        # Error messages (use text contains fallback)
        self.error_user_not_found = page.locator("text=User not found..")
        self.error_email_required = page.locator("text=Email is required")
        self.error_generic_not_found = page.locator("text=not found")

    def enter_email(self, email: str):
        self.email_input.fill(email)

    def click_send_link(self):
        # Click the send link button and wait briefly for any toast/alert or validation
        try:
            self.send_link_button.click()
        except Exception:
            try:
                self.page.locator('button:has-text("Send")').click()
            except Exception:
                return

        # Wait for common feedback elements to appear (best-effort)
        try:
            self.page.wait_for_selector('text=User not found', timeout=3000)
        except Exception:
            try:
                self.page.wait_for_selector('text=not found', timeout=3000)
            except Exception:
                try:
                    self.page.wait_for_selector('[data-sonner-toast]', timeout=2000)
                except Exception:
                    # nothing else to wait for; return and let caller check
                    pass

    def get_visible_errors(self):
        errors = []
        for loc in [self.error_email_required, self.error_user_not_found, self.error_generic_not_found]:
            try:
                if loc.is_visible():
                    errors.append(loc.text_content().strip())
            except Exception:
                continue
        # Check native validation message for email input
        try:
            try:
                vm = self.email_input.evaluate("el => el.validationMessage")
            except Exception:
                vm = ""
            if vm:
                lvm = vm.lower()
                if "include an '@'" in lvm or "missing an '@'" in lvm or "invalid" in lvm:
                    errors.append("Invalid email")
                elif "fill out this field" in lvm or "please fill" in lvm or "required" in lvm:
                    errors.append("Email is required")
                else:
                    errors.append(vm)
        except Exception:
            pass

        # Check role=alert or aria-live regions
        try:
            alerts = self.page.locator('[role="alert"], [aria-live]')
            count = alerts.count()
            for i in range(count):
                try:
                    t = alerts.nth(i).text_content()
                    if t:
                        t = t.strip()
                        if t and t not in errors:
                            errors.append(t)
                except Exception:
                    continue
        except Exception:
            pass

        return errors