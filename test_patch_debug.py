"""Test PATCH with detailed error output."""
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

# Test with simple valid status
print("Testing PATCH with simple status:")
resp = requests.patch(
    f"{BASE_URL}/api/packages/{pkg_uuid}",
    json={"status": "in_transit"}
)

print(f"Status Code: {resp.status_code}")
print(f"Response Headers: {dict(resp.headers)}")
print(f"Response Body:")
print(json.dumps(resp.json(), indent=2))
