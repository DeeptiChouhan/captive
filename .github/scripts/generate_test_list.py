import os
import json
import re

TEST_DIR = "captive/tests"

def parse_test_file(file_path):
    tests = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # match all test_xxx functions
    matches = re.findall(r"def (test_[a-zA-Z0-9_]+)\(", content)

    for m in matches:
        readable = m.replace("test_", "").replace("_", " ").title()
        tests.append({
            "id": m,
            "name": readable,
            "pytest": f"{file_path.replace('/', '.')}::{m}"
        })

    return tests


all_tests = []

for root, dirs, files in os.walk(TEST_DIR):
    for file in files:
        if file.startswith("test_") and file.endswith(".py"):
            all_tests.extend(parse_test_file(os.path.join(root, file)))


output = {"tests": all_tests}

with open("automation_test_list.json", "w") as f:
    json.dump(output, f, indent=4)

print("Generated automation_test_list.json")
