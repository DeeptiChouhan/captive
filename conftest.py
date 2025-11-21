import sys
import os

# Ensure repository root is on sys.path so absolute imports like
# `from pages.login_page import ...` resolve during pytest collection.
ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
