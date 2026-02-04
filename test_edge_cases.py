"""Test various payloads to reproduce the 500 error."""
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

# Test different payloads that might cause 500
test_payloads = [
    {"payload": {}, "name": "Empty object"},
    {"payload": {"status": None}, "name": "Status=None"},
    {"payload": {"status": ""}, "name": "Empty string status"},
    {"payload": {"unknown": "field"}, "name": "Unknown field only"},
    {"payload": None, "name": "No body"},
]

for test in test_payloads:
    print(f"Test: {test['name']}")
    print(f"Payload: {test['payload']}")
    
    try:
        if test['payload'] is None:
            resp = requests.post(f"{BASE_URL}/api/packages/{pkg_uuid}")
        else:
            resp = requests.post(f"{BASE_URL}/api/packages/{pkg_uuid}", json=test['payload'])
        
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Response: {json.dumps(resp.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    print()
