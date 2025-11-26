import time
import json
from pathlib import Path
import os


def _load_template():
    p = Path("data/users.json")
    if p.exists():
        try:
            with p.open() as f:
                data = json.load(f)
            return data.get("new_admin", {})
        except Exception:
            return {}
    return {}


def register_new_user(create_via_api: bool = False, api_url: str | None = None) -> str:
    """Create a new user for tests and return the created email.

    This helper generates a unique email from `data/users.json` ->
    `new_admin` entry by appending a timestamp. If `create_via_api` is True
    and `api_url` (or env var `REG_API_URL`) is provided, it will POST the
    payload to that endpoint. Otherwise it only returns the generated email
    and prints a note — you still need to ensure the system under test sends
    the invitation email that `complete_password_setup` expects.
    """
    entry = _load_template()
    ts = int(time.time())

    email = entry.get("email", f"testuser+{ts}@example.com")
    if "@" in email:
        local, domain = email.split("@", 1)
        local_base = local.split("+")[0]
        generated = f"{local_base}+{ts}@{domain}"
    else:
        generated = f"{email}_{ts}@example.com"

    # Optionally call registration API
    if create_via_api:
        url = api_url or os.getenv("REG_API_URL")
        if url:
            try:
                import requests

                payload = {
                    "email": generated,
                    "firstName": entry.get("firstName", "Auto"),
                    "lastName": entry.get("lastName", "User"),
                    "userName": entry.get("userName", f"user_{ts}")
                }
                resp = requests.post(url, json=payload)
                print("REGISTRATION API ->", resp.status_code, resp.text)
            except Exception as e:
                print("REGISTRATION API call failed:", e)

    print("Generated test user email:", generated)
    return generated
