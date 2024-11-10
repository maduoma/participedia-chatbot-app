# app/routes/main_routes.py

from flask import Blueprint, request, jsonify, session
from app.services.openai_service import classify_query, get_embedding
from app.services.search_service import search_exact_case_method, semantic_search, search_online
from app.utils.text_utils import capitalize_sentences
import logging

# Initialize the blueprint for main routes
main_routes = Blueprint('main_routes', __name__)


# Endpoint to handle user queries
@main_routes.route('/query', methods=['POST'])
def handle_query():
    user_query = request.json.get('query')

    # Check if greeting
    if is_greeting(user_query):
        return jsonify({"response": "Hello! How can I assist you today with Participedia information?"})

    try:
        # Preprocess the query and classify the intent
        processed_query = preprocess_query(user_query)
        logging.debug(f"Processed Query: {processed_query}")

        intent = classify_query(processed_query)
        logging.debug(f"Classified Intent: {intent}")

        # Step 1: Check for specific case/method match
        result = search_exact_case_method(processed_query)
        logging.debug(f"Exact Match Result: {result}")

        # Step 2: If no exact match, perform semantic search based on intent
        if not result:
            if intent == "case":
                result = semantic_search("case", processed_query)
            elif intent == "method":
                result = semantic_search("method", processed_query)
            logging.debug(f"Semantic Search Result: {result}")

        # Step 3: Fallback to online search if no result
        if not result:
            result = search_online(processed_query)
        logging.debug(f"Final Result: {result}")

        # Save response to session memory for chat history
        if 'memory' not in session:
            session['memory'] = []
        session['memory'].append({"query": user_query, "response": result})

        # Capitalize sentences in the description
        if 'description' in result:
            result['description'] = capitalize_sentences(result['description'])

        return jsonify(result)

    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return jsonify({"error": "An error occurred while processing your request"}), 500


# Utility function to preprocess query
def preprocess_query(query):
    from app.utils.text_utils import lemmatize_text
    return lemmatize_text(query.lower())


# Function to identify greetings
def is_greeting(query):
    greetings = ["hi", "hello", "hey", "greetings", "good morning", "good evening"]
    return any(greeting in query.lower() for greeting in greetings)


@main_routes.route('/chat/history', methods=['GET'])
def get_chat_history():
    """
    Retrieve chat history stored in the session for the current user.
    """
    return jsonify(session.get('memory', []))


@main_routes.route('/chat/new', methods=['POST'])
def start_new_chat():
    """
    Clear the existing session memory and start a new chat session.
    """
    session.pop('memory', None)
    return jsonify({"message": "New chat session started."})
