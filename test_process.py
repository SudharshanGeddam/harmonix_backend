"""Test the process endpoint with POST method."""
import requests
import json

# Get a package UUID from the list first
resp = requests.get('http://localhost:8000/api/packages')
packages = resp.json()['packages']

if packages:
    package_uuid = packages[0]['id']
    print(f"Testing with package UUID: {package_uuid}")
    
    # Test POST method (the one used by frontend)
    payload = {
        "weight": 2.5,
        "fragile": True,
        "sender_type": "hospital",
        "claimed_product_type": "medical_supplies"
    }
    
    resp = requests.post(
        f'http://localhost:8000/api/packages/{package_uuid}/process',
        json=payload
    )
    
    print(f"Status Code: {resp.status_code}")
    print(f"Response:")
    print(json.dumps(resp.json(), indent=2))
else:
    print("No packages found. Run seed endpoint first.")
