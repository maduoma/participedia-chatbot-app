# File: test_chatbot.py

import requests

url = "http://127.0.0.1:5001/query"
data = {"query": "Method 146"}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())
