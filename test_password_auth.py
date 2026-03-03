"""
Test script to verify password authentication is working
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("="*70)
print("PASSWORD AUTHENTICATION TEST")
print("="*70)

# Test 1: Login with correct password
print("\n1. Testing Login with Correct Password (admin@example.com / Admin@123)")
print("-" * 70)
try:
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": "admin@example.com", "password": "Admin@123"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 200:
        print("✅ PASS - Login successful with correct password")
        admin_token = response.json()["data"]["token"]
    else:
        print("❌ FAIL - Login should succeed with correct password")
        admin_token = None
except Exception as e:
    print(f"❌ ERROR: {e}")
    admin_token = None

# Test 2: Login with wrong password
print("\n2. Testing Login with Wrong Password")
print("-" * 70)
try:
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": "admin@example.com", "password": "WrongPassword123!"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 401:
        print("✅ PASS - Login correctly rejected with wrong password")
    else:
        print("❌ FAIL - Login should fail with wrong password")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 3: Login without password
print("\n3. Testing Login without Password")
print("-" * 70)
try:
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": "admin@example.com"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 400:
        print("✅ PASS - Login correctly rejected without password")
    else:
        print("❌ FAIL - Login should require password")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 4: Create user with strong password
print("\n4. Testing Create User with Strong Password")
print("-" * 70)
if admin_token:
    try:
        response = requests.post(
            f"{BASE_URL}/users",
            json={
                "name": "Test User",
                "email": "testuser@example.com",
                "age": 25,
                "password": "TestPass@123",
                "role": "user"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        if response.status_code == 201:
            print("✅ PASS - User created with password")
        else:
            print("❌ FAIL - User creation should succeed with valid password")
    except Exception as e:
        print(f"❌ ERROR: {e}")
else:
    print("⏭️  SKIP - No admin token available")

# Test 5: Try to create user without password
print("\n5. Testing Create User without Password")
print("-" * 70)
if admin_token:
    try:
        response = requests.post(
            f"{BASE_URL}/users",
            json={
                "name": "Test User 2",
                "email": "testuser2@example.com",
                "age": 25,
                "role": "user"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        if response.status_code == 400:
            print("✅ PASS - User creation correctly rejected without password")
        else:
            print("❌ FAIL - User creation should require password")
    except Exception as e:
        print(f"❌ ERROR: {e}")
else:
    print("⏭️  SKIP - No admin token available")

# Test 6: Try to create user with weak password
print("\n6. Testing Create User with Weak Password (no uppercase)")
print("-" * 70)
if admin_token:
    try:
        response = requests.post(
            f"{BASE_URL}/users",
            json={
                "name": "Test User 3",
                "email": "testuser3@example.com",
                "age": 25,
                "password": "weak123!",
                "role": "user"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        if response.status_code == 400:
            print("✅ PASS - Weak password correctly rejected")
        else:
            print("❌ FAIL - Weak password should be rejected")
    except Exception as e:
        print(f"❌ ERROR: {e}")
else:
    print("⏭️  SKIP - No admin token available")

# Test 7: Login with newly created user
print("\n7. Testing Login with Newly Created User")
print("-" * 70)
try:
    response = requests.post(
        f"{BASE_URL}/login",
        json={"email": "testuser@example.com", "password": "TestPass@123"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 200:
        print("✅ PASS - Newly created user can login")
    else:
        print("❌ FAIL - User should be able to login")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 8: Try weak password variations
print("\n8. Testing Password Validation Rules")
print("-" * 70)
if admin_token:
    weak_passwords = [
        ("short", "Too short (less than 8 chars)"),
        ("nouppercase1!", "No uppercase letter"),
        ("NOLOWERCASE1!", "No lowercase letter"),
        ("NoDigitsHere!", "No digits"),
        ("NoSpecial123", "No special character"),
    ]
    
    for i, (password, reason) in enumerate(weak_passwords):
        try:
            response = requests.post(
                f"{BASE_URL}/users",
                json={
                    "name": f"Test {i}",
                    "email": f"test{i}@example.com",
                    "age": 25,
                    "password": password
                },
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            if response.status_code == 400:
                print(f"  ✅ {reason}: Correctly rejected")
            else:
                print(f"  ❌ {reason}: Should be rejected")
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
else:
    print("⏭️  SKIP - No admin token available")

print("\n" + "="*70)
print("PASSWORD AUTHENTICATION TEST COMPLETE")
print("="*70)
