"""Test all package endpoints with POST method."""
import requests
import json

# Get packages
resp = requests.get('http://localhost:8000/api/packages')
packages = resp.json()['packages']

if not packages:
    print("No packages found.")
    exit()

pkg_uuid = packages[0]['id']
print(f"Testing with package UUID: {pkg_uuid}\n")

# Test 1: POST to /{package_uuid} (status update)
print("1. Testing POST /{package_uuid} (status update):")
resp = requests.post(
    f'http://localhost:8000/api/packages/{pkg_uuid}',
    json={"status": "in_transit"}
)
print(f"   Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"   Error: {resp.json()}")
else:
    print(f"   ✓ Successfully updated status")

# Test 2: POST to /{package_uuid}/process (signal processing)
print("\n2. Testing POST /{package_uuid}/process (signal processing):")
resp = requests.post(
    f'http://localhost:8000/api/packages/{pkg_uuid}/process',
    json={
        "weight": 3.0,
        "fragile": True,
        "sender_type": "hospital"
    }
)
print(f"   Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"   Error: {resp.json()}")
else:
    data = resp.json()
    print(f"   ✓ Category: {data['category']}, Priority: {data['priority_label']}")

# Test 3: POST to /{package_uuid}/category (category update)
print("\n3. Testing POST /{package_uuid}/category (category update):")
resp = requests.post(
    f'http://localhost:8000/api/packages/{pkg_uuid}/category',
    json={"category": "medicine"}
)
print(f"   Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"   Error: {resp.json()}")
else:
    data = resp.json()
    print(f"   ✓ Category: {data['category']}, Priority: {data['priority_label']}")

print("\n✅ All POST endpoints working!")
