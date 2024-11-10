# File: test_chatbot.py
# Description: This file contains the test cases for the chatbot.

import requests

url = "http://127.0.0.1:5001/query"
data = {"query": "Tell me about case 3."}
response = requests.post(url, json=data)

print("Status Code:", response.status_code)
try:
    print("Response JSON:", response.json())
except requests.exceptions.JSONDecodeError:
    print("Response Text:", response.text)
