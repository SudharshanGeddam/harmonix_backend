"""Verify packages list endpoint."""
import requests
import json

resp = requests.get('http://localhost:8000/api/packages')
data = resp.json()
print(f'Total packages: {data["count"]}')
print('\nFirst package:')
print(json.dumps(data['packages'][0], indent=2))
print(f'\nPackage categories and priorities:')
for pkg in data['packages']:
    print(f"  {pkg['package_id']}: category={pkg['category']}, priority={pkg['priority_label']}")
