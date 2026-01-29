import requests
import time
import os

# Configuration
BASE_URL = 'http://127.0.0.1:8000'
SIGNUP_URL = f'{BASE_URL}/accounts/signup/'
VERIFY_URL = f'{BASE_URL}/accounts/verify-otp/'
OTP_FILE = 'otp_debug.txt'

# Redirect stdout to file
import sys
sys.stdout = open('test_result_internal.log', 'w')

def run_test():
    session = requests.Session()
    
    print("1. Accessing Signup Page...")
    try:
        response = session.get(SIGNUP_URL)
        csrftoken = session.cookies['csrftoken']
        print(f"   Success. CSRF Token: {csrftoken[:10]}...")
    except Exception as e:
        print(f"   Failed to access signup page: {e}")
        return

    # Prepare Signup Data
    import random
    rand_id = random.randint(1000,9999)
    email = f'testuser{rand_id}@example.com'
    print(f"   Using email: {email}")
    
    signup_data = {
        'csrfmiddlewaretoken': csrftoken,
        'name': 'Test User',
        'phone': '1234567890',
        'email': email,
        'place': 'Test Place',
        'password': 'password123',
        'confirm_password': 'password123',
        'role': 'consumer'
    }

    print("2. Submitting Signup Form...")
    response = session.post(SIGNUP_URL, data=signup_data, headers={'Referer': SIGNUP_URL})
    
    if response.url == VERIFY_URL:
        print("   Success. Redirected to verification page.")
    else:
        print(f"   Failed. URL is {response.url}")
        # Print messages from the page
        if "messages" in response.text:
             print("   Found messages in response (partial):")
             print(response.text[:2000]) # Print first 2k chars to see errors
        return

    print("3. retrieving OTP...")
    time.sleep(1) # Wait for file write
    if not os.path.exists(OTP_FILE):
        print("   Failed. OTP file not found.")
        return
        
    with open(OTP_FILE, 'r') as f:
        otp = f.read().strip()
    print(f"   OTP Retrieved: {otp}")

    print("4. Submitting OTP...")
    verify_data = {
        'csrfmiddlewaretoken': session.cookies['csrftoken'],
        'otp': otp
    }
    
    response = session.post(VERIFY_URL, data=verify_data, headers={'Referer': VERIFY_URL})
    
    # Check if redirected to index or some success page
    if response.url == f'{BASE_URL}/':
        print("   SUCCESS! Redirected to Index.")
    elif response.url == f'{BASE_URL}/accounts/login/':
         print("   SUCCESS! Redirected to Login.")
    else:
        print(f"   Failed? URL is {response.url}")
        if "Invalid OTP" in response.text:
            print("   Error: Invalid OTP detected in response.")
        elif "Account created" in response.text:
            print("   Success message found in response content!")

if __name__ == "__main__":
    try:
        run_test()
    finally:
        if os.path.exists(OTP_FILE):
            os.remove(OTP_FILE)
