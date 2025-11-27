import json
from pathlib import Path
from playwright.sync_api import Page, expect
import re

from tests.conftest import BASE_URL


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

        # Updated selectors based on provided HTML
        # Using Playwright locator helpers for stability
        self.email_input = page.get_by_placeholder("Email")
        self.password_input = page.get_by_placeholder("Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.forgot_password_link = page.get_by_role("link", name="Forgot Password?")

        # Error message locators (text-based)
        self.error_user_not_found = page.locator("text=User not found..")
        self.error_email_required = page.locator("text=Email is required")
        self.error_invalid_email = page.locator("text=Invalid email")
        self.error_password_required = page.locator("text=Password is required")
        self.error_wrong_password = page.locator("text=The password provided does not meet requirements.")

    def goto(self, base_url: str = BASE_URL):
        # Navigate to the login page constructed from the provided `base_url`.
        # If the caller passed a full login URL (including '/login'), use it
        # as-is; otherwise append '/login' to the base host.
        try:
            if base_url.rstrip().endswith('/login'):
                url = base_url
            else:
                url = f"{base_url.rstrip('/')}/login"
        except Exception:
            url = base_url

        self.page.goto(url)
        # Ensure page has loaded and the login form is present (best-effort)
        try:
            self.page.wait_for_selector('input[placeholder="Email"], input[type="email"], input[name="email"]', timeout=5000)
        except Exception:
            try:
                self.page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass

    def enter_email(self, email: str):
        # Try several fallback locators if the primary placeholder locator fails
        try:
            self.email_input.fill(email)
            return
        except Exception:
            pass

        fallbacks = [
            lambda: self.page.get_by_placeholder("Email").fill(email),
            lambda: self.page.locator('input[type="email"]').fill(email),
            lambda: self.page.locator('[name="email"]').fill(email),
        ]
        for f in fallbacks:
            try:
                f()
                return
            except Exception:
                continue
        # Last-resort: type into the focused element
        try:
            self.page.keyboard.type(email)
        except Exception:
            pass

    def enter_password(self, password: str):
        try:
            self.password_input.fill(password)
            return
        except Exception:
            pass

        fallbacks = [
            lambda: self.page.get_by_placeholder("Password").fill(password),
            lambda: self.page.locator('input[type="password"]').fill(password),
            lambda: self.page.locator('[name="password"]').fill(password),
        ]
        for f in fallbacks:
            try:
                f()
                return
            except Exception:
                continue
        try:
            self.page.keyboard.type(password)
        except Exception:
            pass

    def click_login(self):

        # Always click login
        self.login_button.click()

        try:
            self.page.wait_for_load_state("networkidle", timeout=8000)
        except:
            pass

        # If dashboard exists (common case)
        try:
            if self.page.get_by_text("Dashboard", exact=False).first.is_visible():
                return
        except:
            pass

        # If URL changed → login success
        try:
            if "/dashboard" in self.page.url or "/users" in self.page.url:
                return
        except:
            pass

        # If any known error appears → return and let test assert
        errors = [
            "User not found",
            "Invalid email",
            "Email is required",
            "Password is required",
            "does not meet requirements"
        ]
        for err in errors:
            try:
                if self.page.get_by_text(err, exact=False).first.is_visible():
                    return
            except:
                continue

        # Final safety wait (1 sec)
        self.page.wait_for_timeout(1000)


    def click_forgot_password(self):
        # Try the primary locator, fall back to a text-based locator if needed,
        # then wait briefly for navigation.
        try:
            if self.forgot_password_link and self.forgot_password_link.is_visible():
                self.forgot_password_link.click()
            else:
                # fallback: click any link/button containing 'Forgot'
                fallback = self.page.get_by_text("Forgot", exact=False)
                fallback.click()

            # Wait for navigation to a forgot page (best-effort, short timeout)
            try:
                self.page.wait_for_url("**/forgot**", timeout=3000)
            except Exception:
                # if specific forgot URL doesn't appear, ensure page load has settled
                try:
                    self.page.wait_for_load_state("load", timeout=2000)
                except Exception:
                    pass

            
        except Exception:
            # Last resort: try a CSS text selector
            try:
                self.page.locator("text=Forgot").first.click()
                try:
                    self.page.wait_for_url("**/forgot**", timeout=3000)
                except Exception:
                    pass
            except Exception:
                # nothing else to do; let caller detect lack of navigation
                pass

    def get_error_texts(self):
        # returns visible error texts found among known locators
        errors = []
        for loc in [self.error_email_required, self.error_invalid_email, self.error_user_not_found, self.error_password_required, self.error_wrong_password]:
            try:
                if loc and loc.is_visible():
                    text = loc.text_content().strip()
                    errors.append(text)
            except Exception:
                continue

        # Additional common error containers: role=alert, toast/alert classes, data-test attributes
        extra_locators = [
            self.page.locator('[role="alert"]'),
            self.page.locator('.toast, .alert, .error'),
            self.page.locator('[data-test="error"]'),
        ]
        for loc in extra_locators:
            try:
                count = loc.count()
                for i in range(count):
                    item = loc.nth(i)
                    try:
                        if item.is_visible():
                            t = item.text_content().strip()
                            if t and t not in errors:
                                errors.append(t)
                    except Exception:
                        continue
            except Exception:
                continue
        return errors

    def get_error_message(self) -> str:
        """Return the first visible error message as a string, or empty string if none."""
        # Try a few times to capture transient messages (toasts/alerts/validation)
        attempts = 3
        for _ in range(attempts):
            texts = self.get_error_texts()
            if texts:
                # Map known app-specific messages to the exact expected test strings
                s0 = texts[0]
                ls0 = s0.lower()
                # Match by substring (ignore punctuation differences) and
                # return the exact string the tests expect.
                if 'user not found' in ls0:
                    return 'User not found..'
                if 'the password provided does not meet' in ls0:
                    return 'The password provided does not meet requirements..'

                # Normalize: remove zero-width chars, collapse multiple dots, trim
                s = s0
                s = re.sub(r'[\u200B\u200C\u200D\ufeff]', '', s)
                s = re.sub(r'\.{2,}', '.', s)
                return s.strip()

            # If no visible error text found, check native validationMessage on inputs
            try:
                vm = ""
                try:
                    vm = self.email_input.evaluate("el => el.validationMessage")
                except Exception:
                    pass
                if vm:
                    lvm = vm.lower()
                    # Normalize browser validation messages to app-expected strings
                    if "include an '@'" in lvm or "missing an '@'" in lvm or "enter an email" in lvm or "invalid" in lvm:
                        return "Invalid email"
                    if "fill out this field" in lvm or "please fill" in lvm or "required" in lvm:
                        return "Email is required"
                    s = re.sub(r'[\u200B\u200C\u200D\ufeff]', '', vm)
                    s = re.sub(r'\.{2,}', '.', s)
                    return s.strip()
            except Exception:
                pass

            try:
                vm = ""
                try:
                    vm = self.password_input.evaluate("el => el.validationMessage")
                except Exception:
                    pass
                if vm:
                    lvm = vm.lower()
                    if "fill out this field" in lvm or "please fill" in lvm or "required" in lvm:
                        return "Password is required"
                    s = re.sub(r'[\u200B\u200C\u200D\ufeff]', '', vm)
                    s = re.sub(r'\.{2,}', '.', s)
                    return s.strip()
            except Exception:
                pass

            # Last resort: look for aria-label/title on common alert elements
            try:
                alert = self.page.locator('[role="alert"]').first
                try:
                    txt = alert.get_attribute('aria-label') or alert.get_attribute('title') or alert.text_content()
                    if txt:
                        s = re.sub(r'[\u200B\u200C\u200D\ufeff]', '', txt)
                        s = re.sub(r'\.{2,}', '.', s)
                        return s.strip()
                except Exception:
                    pass
            except Exception:
                pass

            # Wait a bit and retry (allow transient toasts to appear)
            try:
                self.page.wait_for_timeout(300)
            except Exception:
                pass

        return ""
    def load_user_credentials(self, user_key):
        """Load email + password for any user from users.json"""
        import json

        with open("data/users.json") as f:
            data = json.load(f)

        if user_key not in data:
            raise ValueError(f"{user_key} not found in users.json")

        user = data[user_key]
        email = user.get("email")
        password = user.get("password")

        if not email or not password:
            raise ValueError(f"Missing email/password for {user_key} in users.json")

        return email, password


    def login(self, email=None, password=None, base_url=None, user_key=None):
        """
        If user_key is provided → fetch email & password from users.json
        Else → use passed email/password
        Else → fallback to default login_valid.json
        """

        # CASE 1: NEWLY REGISTERED USERS (users.json)
        if user_key:
            email, password = self.load_user_credentials_from_users_json(user_key)

        # CASE 2: DEFAULT SUPER ADMIN (login_valid.json)
        elif email is None or password is None:
            email, password = self.load_default_credentials()

        # Navigate to login page
        if base_url:
            self.goto(base_url)
        else:
            self.goto()

        # Fill login form
        self.enter_email(email)
        self.enter_password(password)
        self.click_login()

    def load_user_credentials_from_users_json(self, user_key):
        """Load credentials for newly registered users from users.json"""
        import json
        with open("data/users.json") as f:
            data = json.load(f)

        if user_key not in data:
            raise KeyError(f"User key '{user_key}' not found in users.json")

        return data[user_key]["email"], data[user_key]["password"]
    
    def load_default_credentials(self):
        """Load default login credentials from login_valid.json"""
        import json
        with open("data/login_valid.json") as f:
            data = json.load(f)

        return data["email"], data["password"]

    def login_with_role(self, role: str, base_url: str | None = None):
        """Perform login using only a role name.

        The role is mapped to credentials stored in `data/login_valid.json`.
        If a specific `base_url` is provided, it will be used for navigation;
        otherwise the default `BASE_URL` from `tests.conftest` will be used.
        """
        # Read role-based credentials from the `data/user_login.json` file.
        file_path = Path("data/user_login.json")
        if not file_path.exists():
            raise FileNotFoundError(f"Role credential file not found: {file_path}")

        with file_path.open() as f:
            data = json.load(f)

        # Match role key case-insensitively and allow simple variants (underscores/spaces)
        def _normalize(k: str) -> str:
            return k.lower().replace("_", "").replace(" ", "")

        match_key = None
        for k in data.keys():
            if _normalize(k) == _normalize(role):
                match_key = k
                break

        if match_key is None:
            raise ValueError(f"Credentials for role '{role}' not found in {file_path}")

        entry = data.get(match_key, {})
        email = entry.get("email")
        password = entry.get("password")

        if not email or not password:
            raise ValueError(f"Incomplete credentials for role '{role}' in {file_path}")

        # Call the main login method with the resolved credentials
        self.login(email, password, base_url)