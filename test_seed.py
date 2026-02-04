"""Quick test script for seed endpoint."""
import requests
import json

# Test seed endpoint
url = "http://localhost:8000/api/seed/packages"

try:
    response = requests.post(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
