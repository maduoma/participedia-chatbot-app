import requests

# Base URL of the chatbot's endpoints
base_url = "http://127.0.0.1:5001"

# Function to create a new chat session
def create_session(user_id):
    response = requests.post(f"{base_url}/start_new_chat", json={'user_id': user_id})
    if response.status_code == 200:
        data = response.json()
        return data['session_id']
    else:
        print(f"Error: Unable to create session for user '{user_id}'. Status code: {response.status_code}")
        return None

# Function to send a test query
def test_chatbot(query, user_id, session_id):
    url = f"{base_url}/query"
    response = requests.post(url, json={'query': query, 'user_id': user_id, 'session_id': session_id})
    if response.status_code == 200:
        print(f"Query: {query}")
        print("Response:", response.json(), "\n")
    else:
        print(f"Error: Received status code {response.status_code} for query '{query}'")

if __name__ == "__main__":
    user_id = "user_1"
    session_id = create_session(user_id)
    if session_id:
        # List of test queries
        test_queries = [
            "british columbia citizens' assembly on electoral reform",
            "Explain the citizens' assembly case in British Columbia",
            "What was the outcome of the citizens' assembly on electoral reform in British Columbia?",
        ]

        # Run tests for each query
        for query in test_queries:
            test_chatbot(query, user_id, session_id)
    else:
        print("Failed to create a chat session. Tests aborted.")
