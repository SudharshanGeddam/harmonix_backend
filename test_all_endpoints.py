"""Test all update endpoints to find the 500 error."""
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

tests = [
    ("PATCH /packages/{id}", "PATCH", f"/api/packages/{pkg_uuid}", {"status": "in_transit"}),
    ("POST /packages/{id}", "POST", f"/api/packages/{pkg_uuid}", {"status": "delivered"}),
    ("PATCH /packages/{id}/process", "PATCH", f"/api/packages/{pkg_uuid}/process", {"weight": 2.5}),
    ("POST /packages/{id}/process", "POST", f"/api/packages/{pkg_uuid}/process", {"sender_type": "ngo"}),
    ("PATCH /packages/{id}/category", "PATCH", f"/api/packages/{pkg_uuid}/category", {"category": "medicine"}),
    ("POST /packages/{id}/category", "POST", f"/api/packages/{pkg_uuid}/category", {"category": "clothes"}),
]

for name, method, path, payload in tests:
    print(f"Testing {name}")
    try:
        if method == "PATCH":
            resp = requests.patch(f"{BASE_URL}{path}", json=payload)
        else:
            resp = requests.post(f"{BASE_URL}{path}", json=payload)
        
        if resp.status_code == 200:
            print(f"  ✓ 200 OK")
        else:
            print(f"  ✗ {resp.status_code}")
            data = resp.json()
            if 'detail' in data:
                print(f"    {data['detail']}")
    except Exception as e:
        print(f"  ERROR: {e}")
    print()
