# text_chatbot2.py 

import requests

# URL of the chatbot's query endpoint
url = "http://127.0.0.1:5001/query"

# Sample queries for testing
test_queries = [
    {"query": "Tell me about participatory budgeting"},  # Expecting info from 'methods'
    {"query": "Explain the citizens' assembly case in British Columbia"},  # Expecting info from 'cases'
    {"query": "What is collaborative governance?"},  # Method-related query
    {"query": "Tell me about a case on climate action"},  # A general query that may go online
    {"query": "This is an unusual request"},  # Should trigger fallback if not found locally
]


# Function to send a test query
def test_chatbot(query):
    response = requests.post(url, json=query)
    if response.status_code == 200:
        print(f"Query: {query['query']}")
        print("Response:", response.json())
    else:
        print(f"Error: Received status code {response.status_code} for query '{query['query']}'")


# Run tests
for q in test_queries:
    test_chatbot(q)
