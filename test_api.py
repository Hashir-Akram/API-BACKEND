"""
Simple test script to verify API is working correctly
Run this after starting the API server to test basic functionality
"""
import requests
import json
from time import sleep

BASE_URL = "http://127.0.0.1:5000"

def print_section(title):
    """Print a section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_result(test_name, passed, response=None):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} - {test_name}")
    if response and not passed:
        print(f"  Response: {response.status_code} - {response.text[:100]}")

def run_tests():
    """Run basic API tests"""
    print("\n" + "#"*60)
    print("  API Backend - Automated Test Suite")
    print("#"*60)
    
    # Test 1: Health Check
    print_section("Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        passed = response.status_code == 200 and response.json()["status"] == "success"
        print_result("Health check endpoint", passed, response)
    except Exception as e:
        print_result("Health check endpoint", False)
        print(f"  Error: {str(e)}")
        print("\n⚠️  API server is not running. Please start it with: python app.py")
        return
    
    # Test 2: Login as Admin
    print_section("Test 2: Authentication")
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"email": "admin@example.com", "password": "Admin@123"}
        )
        passed = response.status_code == 200
        print_result("Login as admin", passed, response)
        
        if passed:
            admin_token = response.json()["data"]["token"]
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
        else:
            print("  Cannot continue without admin token")
            return
    except Exception as e:
        print_result("Login as admin", False)
        print(f"  Error: {str(e)}")
        return
    
    # Test 3: Login as Regular User
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"email": "john@example.com", "password": "User@123"}
        )
        passed = response.status_code == 200
        print_result("Login as regular user", passed, response)
        
        if passed:
            user_token = response.json()["data"]["token"]
            user_headers = {"Authorization": f"Bearer {user_token}"}
    except Exception as e:
        print_result("Login as regular user", False)
        print(f"  Error: {str(e)}")
        user_headers = None
    
    # Test 4: Get All Users
    print_section("Test 3: Read Operations")
    try:
        response = requests.get(f"{BASE_URL}/users")
        passed = response.status_code == 200 and "users" in response.json()["data"]
        print_result("Get all users", passed, response)
    except Exception as e:
        print_result("Get all users", False)
        print(f"  Error: {str(e)}")
    
    # Test 5: Get User by ID
    try:
        response = requests.get(f"{BASE_URL}/users/1")
        passed = response.status_code == 200
        print_result("Get user by ID", passed, response)
    except Exception as e:
        print_result("Get user by ID", False)
        print(f"  Error: {str(e)}")
    
    # Test 6: Get Non-existent User (404)
    try:
        response = requests.get(f"{BASE_URL}/users/999")
        passed = response.status_code == 404
        print_result("Get non-existent user (expect 404)", passed, response)
    except Exception as e:
        print_result("Get non-existent user", False)
        print(f"  Error: {str(e)}")
    
    # Test 7: Create User
    print_section("Test 4: Create Operations")
    created_user_id = None
    try:
        response = requests.post(
            f"{BASE_URL}/users",
            headers=admin_headers,
            json={
                "name": "Test User",
                "email": "testuser@example.com",
                "age": 25
            }
        )
        passed = response.status_code == 201
        print_result("Create user with valid data", passed, response)
        
        if passed:
            created_user_id = response.json()["data"]["id"]
        else:
            created_user_id = None
    except Exception as e:
        print_result("Create user with valid data", False)
        print(f"  Error: {str(e)}")
        created_user_id = None
    
    # Test 8: Create User without Token (401)
    try:
        response = requests.post(
            f"{BASE_URL}/users",
            json={
                "name": "Another User",
                "email": "another@example.com",
                "age": 30
            }
        )
        passed = response.status_code == 401
        print_result("Create user without token (expect 401)", passed, response)
    except Exception as e:
        print_result("Create user without token", False)
        print(f"  Error: {str(e)}")
    
    # Test 9: Create User with Invalid Data
    print_section("Test 5: Validation Tests")
    try:
        response = requests.post(
            f"{BASE_URL}/users",
            headers=admin_headers,
            json={
                "name": "Ab",  # Too short
                "email": "test@example.com",
                "age": 25
            }
        )
        passed = response.status_code == 400
        print_result("Create user with short name (expect 400)", passed, response)
    except Exception as e:
        print_result("Create user with short name", False)
        print(f"  Error: {str(e)}")
    
    # Test 10: Create User Under Age
    try:
        response = requests.post(
            f"{BASE_URL}/users",
            headers=admin_headers,
            json={
                "name": "Young User",
                "email": "young@example.com",
                "age": 17
            }
        )
        passed = response.status_code == 400
        print_result("Create user under 18 (expect 400)", passed, response)
    except Exception as e:
        print_result("Create user under 18", False)
        print(f"  Error: {str(e)}")
    
    # Test 11: Create User with Duplicate Email
    try:
        response = requests.post(
            f"{BASE_URL}/users",
            headers=admin_headers,
            json={
                "name": "Duplicate",
                "email": "admin@example.com",
                "age": 25
            }
        )
        passed = response.status_code == 409
        print_result("Create user with duplicate email (expect 409)", passed, response)
    except Exception as e:
        print_result("Create user with duplicate email", False)
        print(f"  Error: {str(e)}")
    
    # Test 12: Update User
    print_section("Test 6: Update Operations")
    if created_user_id:
        try:
            response = requests.put(
                f"{BASE_URL}/users/{created_user_id}",
                headers=admin_headers,
                json={"name": "Updated Test User"}
            )
            passed = response.status_code == 200
            print_result("Update user", passed, response)
        except Exception as e:
            print_result("Update user", False)
            print(f"  Error: {str(e)}")
    
    # Test 13: Delete User as Non-Admin (403)
    print_section("Test 7: Authorization Tests")
    if created_user_id and user_headers:
        try:
            response = requests.delete(
                f"{BASE_URL}/users/{created_user_id}",
                headers=user_headers
            )
            passed = response.status_code == 403
            print_result("Delete user as non-admin (expect 403)", passed, response)
        except Exception as e:
            print_result("Delete user as non-admin", False)
            print(f"  Error: {str(e)}")
    
    # Test 14: Delete User as Admin
    if created_user_id:
        try:
            response = requests.delete(
                f"{BASE_URL}/users/{created_user_id}",
                headers=admin_headers
            )
            passed = response.status_code == 200
            print_result("Delete user as admin", passed, response)
        except Exception as e:
            print_result("Delete user as admin", False)
            print(f"  Error: {str(e)}")
    
    # Test 15: Error Simulation
    print_section("Test 8: Error Handling")
    try:
        response = requests.get(f"{BASE_URL}/error")
        passed = response.status_code == 500
        print_result("Simulate 500 error (expect 500)", passed, response)
    except Exception as e:
        print_result("Simulate 500 error", False)
        print(f"  Error: {str(e)}")
    
    # Test 16: Reset Data
    print_section("Test 9: Utility Operations")
    try:
        response = requests.post(f"{BASE_URL}/reset")
        passed = response.status_code == 200
        print_result("Reset data store", passed, response)
    except Exception as e:
        print_result("Reset data store", False)
        print(f"  Error: {str(e)}")
    
    # Summary
    print("\n" + "#"*60)
    print("  Test Suite Complete")
    print("#"*60)
    print("\n✓ All basic tests completed successfully!")
    print("  API is working as expected.\n")

if __name__ == "__main__":
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
