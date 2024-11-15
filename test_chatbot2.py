# File: test_chatbot2.py

import requests

# URL of the chatbot's query endpoint
url = "http://127.0.0.1:5001/query"

# Sample queries for testing, including different `user_id`s to test session management
test_queries = [
    {"user_id": "user_1", "query": "Tell me about Civicus World Assembly"}, 
    {"user_id": "user_1", "query": "Tell me about participatory budgeting"},  # Expecting info from 'methods'
    {"user_id": "user_1", "query": "Explain the citizens' assembly case in British Columbia"},  # Expecting info from 'cases'
    {"user_id": "user_2", "query": "What is collaborative governance?"},  # Method-related query with a new user
    {"user_id": "user_2", "query": "Tell me about a case on climate action"},  # General query for the same new user
    {"user_id": "user_1", "query": "This is an unusual request"},  # Should trigger fallback if not found locally
    {"user_id": "user_1", "query": "Tell me about case 3."},  # Expecting info from case 3, including URL
    {"user_id": "user_1", "query": "Tell me about Method 146."},  # Expecting info from method 3, including URL
    {"user_id": "user_1", "query": "Tell me about Method 3."}  # Expecting info from method 3, including URL
]

# Function to send a test query
def test_chatbot(query):
    response = requests.post(url, json=query)
    if response.status_code == 200:
        print(f"Query: {query['query']}")
        print("Response:", response.json())
    else:
        print(f"Error: Received status code {response.status_code} for query '{query['query']}'")


# Run tests for each query
for q in test_queries:
    test_chatbot(q)