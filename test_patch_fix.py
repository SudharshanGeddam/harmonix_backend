"""Test the PATCH endpoint with flexible status validation."""
import requests
import json

BASE_URL = "http://localhost:8001"

# Get first package
resp = requests.get(f"{BASE_URL}/api/packages")
packages = resp.json()['packages']

if not packages:
    print("No packages found")
    exit()

pkg_uuid = packages[0]['id']
print(f"Testing PATCH with package UUID: {pkg_uuid}\n")

# Test 1: Valid status (lowercase)
print("1. Testing PATCH with valid status (in_transit):")
resp = requests.patch(
    f"{BASE_URL}/api/packages/{pkg_uuid}",
    json={"status": "in_transit"}
)
print(f"   Status Code: {resp.status_code}")
if resp.status_code != 200:
    print(f"   Error: {resp.json()}")
else:
    print(f"   ✓ Success")

# Test 2: Valid status (mixed case)
print("\n2. Testing PATCH with mixed case status (DELIVERED):")
resp = requests.patch(
    f"{BASE_URL}/api/packages/{pkg_uuid}",
    json={"status": "DELIVERED"}
)
print(f"   Status Code: {resp.status_code}")
if resp.status_code != 200:
    print(f"   Error: {resp.json()}")
else:
    print(f"   ✓ Success")

# Test 3: Valid status with extra spaces
print("\n3. Testing PATCH with spaces ( delayed ):")
resp = requests.patch(
    f"{BASE_URL}/api/packages/{pkg_uuid}",
    json={"status": " delayed "}
)
print(f"   Status Code: {resp.status_code}")
if resp.status_code != 200:
    print(f"   Error: {resp.json()}")
else:
    print(f"   ✓ Success")

# Test 4: Invalid status
print("\n4. Testing PATCH with invalid status (should fail):")
resp = requests.patch(
    f"{BASE_URL}/api/packages/{pkg_uuid}",
    json={"status": "invalid_status"}
)
print(f"   Status Code: {resp.status_code}")
if resp.status_code == 422:
    print(f"   ✓ Correctly rejected with validation error")
else:
    print(f"   Response: {resp.json()}")

print("\n✅ Tests completed!")
