import unittest
import requests

BASE_URL = "http://127.0.0.1:5001"

class ChatbotAPITest(unittest.TestCase):

    def test_file_upload(self):
        files = [
            ('file', ('Case Dataset.csv', open('raw_clean_data/Case Dataset.csv', 'rb'), 'text/csv')),
            ('file', ('Method Dataset.csv', open('raw_clean_data/Method Dataset.csv', 'rb'), 'text/csv'))
        ]
        response = requests.post(f"{BASE_URL}/upload", files=files)
        self.assertEqual(response.status_code, 200, "File upload failed")
        print("File upload successful.")

    def test_chat_query(self):
        payload = {
            "user_id": "test_user",
            "query": "Tell me about participatory budgeting"
        }
        response = requests.post(f"{BASE_URL}/query", json=payload)
        self.assertEqual(response.status_code, 200, "Chat query failed")
        print("Chat query response:", response.json())

    def test_chat_history_retrieval(self):
        session_id = 1  # Replace with an actual session ID from your database
        response = requests.get(f"{BASE_URL}/chat_history/{session_id}")
        self.assertEqual(response.status_code, 200, "Chat history retrieval failed")
        print("Chat history for session:", response.json())

if __name__ == "__main__":
    unittest.main()
