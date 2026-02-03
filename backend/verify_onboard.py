import requests
import os

BASE_URL = "http://127.0.0.1:8000/api"

# Create a dummy pdf
with open("dummy_resume.pdf", "wb") as f:
    f.write(b"%PDF-1.4 header")

def run_verification():
    print("1. Registering User...")
    email = "test_onboard@example.com"
    password = "password123"
    username = "test_onboard"
    
    # Register/Login
    session = requests.Session()
    
    # Try login first in case user exists
    login_data = {
        "email": email,
        "password": password
    }
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    
    if response.status_code == 200:
        print("   User exists, logged in.")
        token = response.json()['tokens']['access']
    else:
        # Register
        reg_data = {
            "email": email,
            "password": password,
            "name": "Test User",
            "username": username
        }
        response = requests.post(f"{BASE_URL}/auth/register/", json=reg_data)
        if response.status_code != 201:
            print(f"   Registration failed: {response.text}")
            return
        print("   User registered.")
        token = response.json()['tokens']['access']

    headers = {"Authorization": f"Bearer {token}"}

    print("\n2. Submitting Onboarding Data...")
    files = {'resume': open('dummy_resume.pdf', 'rb')}
    data = {
        "institution": "AI University",
        "profession": "Developer",
        "experience": "2 years",
        "gender": "Male",
        "phone_number": "1234567890",
        "graduation_year": 2024
    }
    
    response = requests.post(f"{BASE_URL}/onboard/", headers=headers, data=data, files=files)
    if response.status_code in [201, 200]: # 201 created, or maybe we handle re-submission
        print(f"   Success: {response.status_code}")
    elif response.status_code == 400 and "already onboarded" in response.text:
         print("   User already onboarded (Expected if re-running)")
    else:
        print(f"   Failed: {response.status_code} - {response.text}")

    print("\n3. Fetching Onboarding Data...")
    response = requests.get(f"{BASE_URL}/onboard/", headers=headers)
    if response.status_code == 200:
        print(f"   Data: {response.json()}")
    else:
        print(f"   Failed to fetch: {response.status_code}")

    print("\n4. Updating Onboarding Data...")
    update_data = {"profession": "Senior Developer"}
    response = requests.patch(f"{BASE_URL}/onboard/", headers=headers, data=update_data)
    if response.status_code == 200:
        print(f"   Updated Data: {response.json()['profession']}")
    else:
        print(f"   Update failed: {response.status_code}")

    # Clean up
    if os.path.exists("dummy_resume.pdf"):
        os.remove("dummy_resume.pdf")

if __name__ == "__main__":
    run_verification()
