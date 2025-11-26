import requests
BASE_API_URL = "https://captive-api.encoreskydev.com/api/v1/users/public/delete-by-email"

def read_json(path):
    import json
    with open(path, 'r') as f:
        return json.load(f)
    
def delete_user_if_exists(email: str):
    """
    Deletes the user using DELETE-BY-EMAIL API before test execution.
    Does nothing if the user doesn't exist.
    """
    payload = {"email": email}
    headers = {"Content-Type": "application/json", "accept": "application/json"}

    response = requests.post(BASE_API_URL, json=payload, headers=headers)

    # Log output only for debugging – does NOT fail test
    print(f"DELETE-USER API → Status: {response.status_code} | Message: {response.text}")

    return response
def setup_test_user(email: str):
    """ Setup test user by deleting if exists before test execution.
    """
    delete_user_if_exists(email)            