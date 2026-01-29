import requests
import time

BASE_URL = 'http://127.0.0.1:8000'
SIGNUP_URL = f'{BASE_URL}/accounts/signup/'
VERIFY_URL = f'{BASE_URL}/accounts/verify-otp/'

session = requests.Session()

print("=" * 50)
print("TESTING OTP VERIFICATION FLOW")
print("=" * 50)

# Step 1: Get CSRF token
print("\n[1/4] Getting signup page...")
response = session.get(SIGNUP_URL)
csrftoken = session.cookies['csrftoken']
print(f"   ✓ CSRF Token obtained")

# Step 2: Submit signup
import random
test_id = random.randint(10000, 99999)
email = f'test{test_id}@example.com'

signup_data = {
    'csrfmiddlewaretoken': csrftoken,
    'name': 'Test User',
    'phone': '9876543210',
    'email': email,
    'place': 'Kerala',
    'password': 'password123',
    'confirm_password': 'password123',
    'role': 'consumer'
}

print(f"\n[2/4] Submitting signup for {email}...")
response = session.post(SIGNUP_URL, data=signup_data, headers={'Referer': SIGNUP_URL}, allow_redirects=True)

if 'verify-otp' in response.url:
    print(f"   ✓ Redirected to OTP verification page")
else:
    print(f"   ✗ Failed to redirect. URL: {response.url}")
    exit(1)

# Step 3: Get OTP from file
print("\n[3/4] Reading OTP from debug file...")
time.sleep(0.5)
try:
    with open('otp_debug.txt', 'r') as f:
        otp = f.read().strip()
    print(f"   ✓ OTP retrieved: {otp}")
except FileNotFoundError:
    print("   ✗ OTP file not found")
    exit(1)

# Step 4: Submit OTP
verify_data = {
    'csrfmiddlewaretoken': session.cookies.get('csrftoken'),
    'otp': otp
}

print(f"\n[4/4] Submitting OTP for verification...")
response = session.post(VERIFY_URL, data=verify_data, headers={'Referer': VERIFY_URL}, allow_redirects=True)

if response.url == f'{BASE_URL}/':
    print(f"   ✓ Verification successful! Redirected to index page")
    print("\n" + "=" * 50)
    print("✓ ALL TESTS PASSED!")
    print("=" * 50)
elif 'Invalid OTP' in response.text:
    print(f"   ✗ OTP verification failed")
    print(f"   Error: Invalid OTP")
else:
    print(f"   ? Unexpected result. URL: {response.url}")
    if 'Account created' in response.text:
        print("   Note: Success message found in response")
