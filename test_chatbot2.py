import requests

# Base URL of the chatbot application
BASE_URL = "http://127.0.0.1:5001"

# Sample queries for testing, including different user_ids to test session management
test_queries = [
    {"user_id": "user_1", "query": "Tell me about participatory budgeting"},  # Method-related query
    {"user_id": "user_1", "query": "Explain the citizens' assembly case in British Columbia"},  # Case-related query
    {"user_id": "user_2", "query": "What is collaborative governance?"},  # Method-related query with a new user
    {"user_id": "user_2", "query": "Tell me about a case on climate action"},  # General query for the same new user
    {"user_id": "user_1", "query": "This is an unusual request"},  # Should trigger fallback if not found locally
    {"user_id": "user_1", "query": "Tell me about case 3."},  # Expecting info from case 3, including URL
    {"user_id": "user_1", "query": "Tell me about Method 3."}  # Expecting info from method 3
]

# Function to send a test query to the chatbot
def test_chat_query(query):
    response = requests.post(f"{BASE_URL}/query", json=query)
    if response.status_code == 200:
        print(f"Query: {query['query']}")
        print("Response:", response.json())
    else:
        print(f"Error: Received status code {response.status_code} for query '{query['query']}'")

# Function to upload files to the chatbot
def test_file_upload(file_paths):
    files = [('file', (file_path, open(file_path, 'rb'), 'text/csv')) for file_path in file_paths]
    response = requests.post(f"{BASE_URL}/upload", files=files)
    if response.status_code == 200:
        print("File upload successful.")
    else:
        print(f"Error: Received status code {response.status_code} for file upload")

# Function to retrieve chat history for a given session ID
def test_chat_history(session_id):
    response = requests.get(f"{BASE_URL}/chat_history/{session_id}")
    if response.status_code == 200:
        print(f"Chat history for session {session_id}:")
        for entry in response.json():
            print(f"Query: {entry['query']}")
            print(f"Response: {entry['response']}")
            print(f"Timestamp: {entry['created_at']}")
            print("------")
    else:
        print(f"Error: Received status code {response.status_code} for retrieving chat history")

# Test chat queries
print("Testing chat queries:")
for query in test_queries:
    test_chat_query(query)

# Test file upload (ensure these files exist in the specified path)
print("\nTesting file upload:")
test_file_upload(['raw_clean_data/Case Dataset.csv', 'raw_clean_data/Method Dataset.csv'])

# Test retrieving chat history for a specific session ID (replace with an actual session ID from your database)
print("\nTesting chat history retrieval:")
test_chat_history(1)  # Replace `1` with a valid session ID for your tests
