def assert_text(actual, expected):
    assert (actual or '').strip() == (expected or '').strip(), f"Expected '{expected}', got '{actual}'"