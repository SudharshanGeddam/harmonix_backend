"""Test the business sender type fix."""
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
print(f"Testing with package: {pkg_uuid}\n")

# Test with "business" sender type (the problematic payload from frontend)
print("Test: PATCH /process with sender_type='business'")
payload = {
    "weight": 45,
    "fragile": False,
    "sender_type": "business",
    "claimed_product_type": "medical"
}
print(f"Payload: {json.dumps(payload, indent=2)}")

resp = requests.patch(f"{BASE_URL}/api/packages/{pkg_uuid}/process", json=payload)

print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"✓ Success!")
    print(f"  Category: {data['category']}")
    print(f"  Priority: {data['priority_label']}")
else:
    print(f"✗ Failed")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
