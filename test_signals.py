"""Test PackageProcessSignals with various input combinations."""
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
print(f"Testing PATCH /api/packages/{pkg_uuid}/process\n")
print("=" * 70)

test_cases = [
    {
        "name": "Test 1: All fields",
        "payload": {
            "weight": 2.5,
            "fragile": True,
            "sender_type": "hospital",
            "claimed_product_type": "medical_supplies",
            "zk_verified_sender": False
        }
    },
    {
        "name": "Test 2: Only weight",
        "payload": {"weight": 3.0}
    },
    {
        "name": "Test 3: Sender type only",
        "payload": {"sender_type": "ngo"}
    },
    {
        "name": "Test 4: Fragile and claimed product",
        "payload": {
            "fragile": True,
            "claimed_product_type": "medical_supplies"
        }
    },
    {
        "name": "Test 5: Empty body (all optional)",
        "payload": {}
    },
    {
        "name": "Test 6: Extra fields (should be ignored)",
        "payload": {
            "weight": 1.5,
            "unknown_field": "should_be_ignored",
            "another_extra": 123
        }
    }
]

for test in test_cases:
    print(f"\n{test['name']}")
    print(f"Payload: {json.dumps(test['payload'], indent=2)}")
    
    resp = requests.patch(
        f"{BASE_URL}/api/packages/{pkg_uuid}/process",
        json=test['payload']
    )
    
    print(f"Status Code: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"✓ Success!")
        print(f"  Category: {data['category']}, Priority: {data['priority_label']}")
    else:
        print(f"✗ Failed")
        error = resp.json()
        if 'detail' in error:
            print(f"  Error: {error['detail']}")

print("\n" + "=" * 70)
print("✅ All tests completed!")
