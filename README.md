# captive_final - Playwright + Python + Pytest Login Automation Framework

Base URL: https://captive.encoreskydev.com/login

## Structure
```
captive_final/
├── tests/
│   ├── test_login_positive.py
│   ├── test_login_negative.py
│   ├── test_forgot_password.py
│   └── conftest.py
├── pages/
│   ├── login_page.py
│   └── forgot_password_page.py
├── data/
│   ├── login_valid.json
│   └── login_invalid.json
├── utils/
│   ├── helpers.py
│   └── assertions.py
├── pytest.ini
└── requirements.txt
```

## How to run
1. Create and activate a virtual environment (recommended).
2. Install dependencies:
   ```
   pip install -r requirements.txt
   playwright install
   ```
3. Run tests:
   ```
   pytest -v -s
   ```