# File: test_hello.py

import requests

url = "http://127.0.0.1:5001/query"
data = {"query": "Greetings!"}
response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())
