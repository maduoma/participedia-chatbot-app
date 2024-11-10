# app/services/openai_service.py

import openai
import logging
from config import Config

# Initialize OpenAI client with API key from config
client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

# Set up logging for OpenAI API interactions
logging.basicConfig(level=logging.DEBUG)


def classify_query(query):
    """
    Uses OpenAI's GPT model to classify a user query as 'case', 'method', or 'general'.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Classify the user query into either 'case', 'method', or 'general'. Respond with only one word: 'case', 'method', or 'general'.",
                },
                {"role": "user", "content": query},
            ],
        )
        intent = response['choices'][0]['message']['content'].strip().lower()
        # Ensure intent is one of the expected values
        if intent not in ["case", "method", "general"]:
            intent = "general"
        logging.debug(f"Classified Intent: {intent}")
        return intent
    except Exception as e:
        logging.error(f"OpenAI API error in classify_query: {e}")
        return "general"


def get_embedding(text):
    """
    Generates a semantic embedding for a given text using OpenAI's embedding API.
    """
    try:
        response = client.embeddings.create(
            input=text, model="text-embedding-ada-002"
        )
        embedding = response['data'][0]['embedding']
        logging.debug(f"Generated embedding for text: {embedding}")
        return embedding
    except Exception as e:
        logging.error(f"OpenAI API error in get_embedding: {e}")
        return None
