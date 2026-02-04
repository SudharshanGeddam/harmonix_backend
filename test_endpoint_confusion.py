"""Test to understand what the frontend is doing wrong."""
import requests
import json

BASE_URL = "http://localhost:8001"

# Get packages
resp = requests.get(f"{BASE_URL}/api/packages")
packages = resp.json()['packages']

if not packages:
    print("No packages")
    exit()

pkg_uuid = packages[0]['id']
print(f"Package UUID: {pkg_uuid}\n")

# Test 1: The payload frontend is sending (to WRONG endpoint)
print("Test 1: Frontend sending signals payload to status update endpoint (WRONG)")
wrong_payload = {
    "weight": 45,
    "fragile": False,
    "sender_type": "business",
    "claimed_product_type": "medical"
}
print(f"Endpoint: PATCH /api/packages/{pkg_uuid}")
print(f"Payload: {json.dumps(wrong_payload, indent=2)}")

resp = requests.patch(f"{BASE_URL}/api/packages/{pkg_uuid}", json=wrong_payload)
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Error: {resp.json()['detail']}")
print()

# Test 2: The RIGHT endpoint for signals
print("Test 2: Sending signals to CORRECT endpoint (/process)")
print(f"Endpoint: PATCH /api/packages/{pkg_uuid}/process")
print(f"Payload: {json.dumps(wrong_payload, indent=2)}")

resp = requests.patch(f"{BASE_URL}/api/packages/{pkg_uuid}/process", json=wrong_payload)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"✓ Success! Category: {resp.json()['category']}")
else:
    print(f"Error: {resp.json()['detail']}")
print()

# Test 3: Correct status update endpoint
print("Test 3: Correct status update to status endpoint")
status_payload = {"status": "in_transit"}
print(f"Endpoint: PATCH /api/packages/{pkg_uuid}")
print(f"Payload: {json.dumps(status_payload, indent=2)}")

resp = requests.patch(f"{BASE_URL}/api/packages/{pkg_uuid}", json=status_payload)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"✓ Success!")
else:
    print(f"Error: {resp.json()['detail']}")
