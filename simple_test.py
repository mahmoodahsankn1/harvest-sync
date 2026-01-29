import requests
import time

BASE_URL = 'http://127.0.0.1:8000'
SIGNUP_URL = f'{BASE_URL}/accounts/signup/'

session = requests.Session()

# Get CSRF token
response = session.get(SIGNUP_URL)
csrftoken = session.cookies['csrftoken']
print(f"CSRF Token: {csrftoken[:20]}...")

# Signup data
signup_data = {
    'csrfmiddlewaretoken': csrftoken,
    'name': 'Test User',
    'phone': '9876543210',
    'email': 'test999@example.com',
    'place': 'Test Place',
    'password': 'password123',
    'confirm_password': 'password123',
    'role': 'consumer'
}

print("\nSubmitting signup form...")
response = session.post(SIGNUP_URL, data=signup_data, headers={'Referer': SIGNUP_URL})

print(f"Response URL: {response.url}")
print(f"Status Code: {response.status_code}")

# Check for messages in response
if 'Failed to send OTP' in response.text:
    print("\nERROR: Email sending failed")
elif 'OTP sent to' in response.text:
    print("\nSUCCESS: OTP was sent")
elif 'User with this email already exists' in response.text:
    print("\nERROR: User already exists")
else:
    print("\nChecking response content...")
    # Look for error indicators
    if 'alert' in response.text or 'error' in response.text.lower():
        print("Found potential error in response")
        
# Check if OTP file was created
time.sleep(0.5)
try:
    with open('otp_debug.txt', 'r') as f:
        otp = f.read()
        print(f"\nOTP file created: {otp}")
except FileNotFoundError:
    print("\nOTP file NOT created - email send failed")
