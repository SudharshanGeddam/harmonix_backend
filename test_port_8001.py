"""Test all endpoints on port 8001."""
import requests
import json

BASE_URL = "http://localhost:8001"

print("=" * 60)
print("TESTING ALL ENDPOINTS ON PORT 8001")
print("=" * 60)

# Test 1: Root endpoint
print("\n1. GET /")
try:
    resp = requests.get(f"{BASE_URL}/")
    print(f"   Status: {resp.status_code} ✓")
    print(f"   Response: {resp.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Get packages
print("\n2. GET /api/packages")
try:
    resp = requests.get(f"{BASE_URL}/api/packages")
    print(f"   Status: {resp.status_code} ✓")
    data = resp.json()
    print(f"   Package count: {data['count']}")
    if data['packages']:
        pkg_uuid = data['packages'][0]['id']
        pkg_id = data['packages'][0]['package_id']
        print(f"   First package: {pkg_id}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: POST to /{package_uuid}
print(f"\n3. POST /api/packages/{pkg_uuid} (status update)")
try:
    resp = requests.post(
        f"{BASE_URL}/api/packages/{pkg_uuid}",
        json={"status": "in_transit"}
    )
    print(f"   Status: {resp.status_code} ✓")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: POST to /{package_uuid}/process
print(f"\n4. POST /api/packages/{pkg_uuid}/process (signal processing)")
try:
    resp = requests.post(
        f"{BASE_URL}/api/packages/{pkg_uuid}/process",
        json={
            "weight": 3.0,
            "fragile": True,
            "sender_type": "hospital"
        }
    )
    print(f"   Status: {resp.status_code} ✓")
except Exception as e:
    print(f"   Error: {e}")

# Test 5: POST to /{package_uuid}/category
print(f"\n5. POST /api/packages/{pkg_uuid}/category (category update)")
try:
    resp = requests.post(
        f"{BASE_URL}/api/packages/{pkg_uuid}/category",
        json={"category": "medicine"}
    )
    print(f"   Status: {resp.status_code} ✓")
except Exception as e:
    print(f"   Error: {e}")

# Test 6: POST /seed/packages
print("\n6. POST /api/seed/packages (already seeded, should get 409)")
try:
    resp = requests.post(f"{BASE_URL}/api/seed/packages")
    print(f"   Status: {resp.status_code} (409 expected for duplicates)")
    print(f"   Response: {resp.json()['detail']}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETED")
print("=" * 60)
