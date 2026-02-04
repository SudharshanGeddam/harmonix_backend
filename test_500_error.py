"""Test to reproduce 500 error."""
import requests
import json

BASE_URL = "http://localhost:8001"

print("Getting packages...")
resp = requests.get(f"{BASE_URL}/api/packages")
packages = resp.json()['packages']

if not packages:
    print("No packages found")
    exit()

pkg_uuid = packages[0]['id']
print(f"Package UUID: {pkg_uuid}\n")

# Try the problematic endpoint with empty body
print("Test 1: Calling PATCH /process with empty body")
resp = requests.patch(f"{BASE_URL}/api/packages/{pkg_uuid}/process", json={})
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
print()

# Try with only weight
print("Test 2: Calling PATCH /process with weight only")
resp = requests.patch(f"{BASE_URL}/api/packages/{pkg_uuid}/process", json={"weight": 2.5})
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
