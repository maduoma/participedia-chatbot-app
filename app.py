# File: app.py

from config import Config
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import openai
import requests
import re
import spacy
from sklearn.metrics.pairwise import cosine_similarity
import logging
from nltk.tokenize import sent_tokenize
import nltk
from flask_migrate import Migrate

# Download the 'punkt' tokenizer models
nltk.download('punkt')

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Load the spaCy English model
nlp = spacy.load('en_core_web_sm')

# Initialize Flask app and configure database
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY  # For session management
db = SQLAlchemy(app)



# After initializing the app and db
migrate = Migrate(app, db)


# Set up OpenAI and SerpAPI keys
client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
serpapi_key = Config.SERPAPI_API_KEY


# SQLAlchemy Models for Cases, Methods, ChatSessions, and ChatHistories
class Case(db.Model):
    __tablename__ = 'cases'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String, nullable=True)


class Method(db.Model):
    __tablename__ = 'methods'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String, nullable=True)


class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)  # Use unique identifier for each user
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    histories = db.relationship('ChatHistory', backref='session', lazy=True)


class ChatHistory(db.Model):
    __tablename__ = 'chat_histories'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    query = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


# Function to get or create a chat session
def get_or_create_session(user_id):
    session_record = ChatSession.query.filter_by(user_id=user_id).first()
    if not session_record:
        session_record = ChatSession(user_id=user_id)
        db.session.add(session_record)
        db.session.commit()
    return session_record


# Function to capitalize the first letter of each sentence
def capitalize_sentences(text):
    sentences = sent_tokenize(text)
    capitalized_sentences = [sentence.capitalize() for sentence in sentences]
    return ' '.join(capitalized_sentences)


# Function to check if a query is a greeting
def is_greeting(query):
    greetings = ["hi", "hello", "hey", "greetings",
                 "good morning", "good evening"]
    return any(greeting in query.lower() for greeting in greetings)


# Endpoint to handle user queries
@app.route('/query', methods=['POST'])
def handle_query():
    user_query = request.json.get('query')
    user_id = request.json.get('user_id', 'default_user')  # Default user_id if not provided

    # Get or create a session for the user
    chat_session = get_or_create_session(user_id)

    # Check for greeting
    if is_greeting(user_query):
        response_text = "Hello! How can I assist you today about Participedia?"
        save_chat_history(chat_session.id, user_query, response_text)
        return jsonify({"response": response_text})

    try:
        # Preprocess the query
        processed_query = preprocess_query(user_query)
        logging.debug(f"Processed Query: {processed_query}")

        # Step 1: Use OpenAI API for NLP-based intent classification
        intent = classify_query(processed_query)
        logging.debug(f"Classified Intent: {intent}")

        # Step 2: Check for specific case/method match
        result = search_exact_case_method(processed_query)
        logging.debug(f"Exact Match Result: {result}")

        # Step 3: If no exact match, perform semantic search based on intent
        if not result:
            if intent == "case":
                result = semantic_search(Case, processed_query)
            elif intent == "method":
                result = semantic_search(Method, processed_query)
            logging.debug(f"Semantic Search Result: {result}")

        # Step 4: Fallback to online search if no result
        if not result:
            result = search_online(processed_query)
        logging.debug(f"Final Result: {result}")

        # Capitalize the first letter of each sentence in the description
        if 'description' in result:
            result['description'] = capitalize_sentences(result['description'])

        # Save chat history
        save_chat_history(chat_session.id, user_query, result.get('description', 'No response found'))

        return jsonify(result)

    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return jsonify({"error": "An error occurred while processing your request"}), 500


# Function to save chat history
def save_chat_history(session_id, query, response):
    chat_history = ChatHistory(session_id=session_id, query=query, response=response)
    db.session.add(chat_history)
    db.session.commit()


# Function to preprocess the query
def preprocess_query(query):
    # Use spaCy for tokenization and lemmatization
    doc = nlp(query.lower())
    lemmatized_tokens = [
        token.lemma_ for token in doc if not token.is_punct and not token.is_space
    ]
    return ' '.join(lemmatized_tokens)


# Function to classify the query intent
def classify_query(query):
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
        return intent
    except Exception as e:
        logging.error(f"OpenAI API error in classify_query: {e}")
        return "general"


# Function to search for an exact match in cases or methods
def search_exact_case_method(query):
    case_match = re.search(r'\bcase\s+(\d+)\b', query, re.IGNORECASE)
    method_match = re.search(r'\bmethod\s+(\d+)\b', query, re.IGNORECASE)

    if case_match:
        case_id = int(case_match.group(1))
        result = db.session.get(Case, case_id)
        if result:
            return {
                "title": result.title,
                "description": capitalize_sentences(result.description) if result.description else '',
                "url": result.url,
                "source": "internal",
            }

    if method_match:
        method_id = int(method_match.group(1))
        result = db.session.get(Method, method_id)
        if result:
            return {
                "title": result.title,
                "description": capitalize_sentences(result.description) if result.description else '',
                "url": result.url,
                "source": "internal",
            }

    return None


# Function to perform a semantic search
def semantic_search(model, query):
    entries = model.query.all()
    query_embedding = get_embedding(query)

    if not query_embedding:
        return None

    best_match = None
    highest_similarity = -1

    for entry in entries:
        entry_text = f"{entry.title} {entry.description}"
        entry_embedding = get_embedding(entry_text)
        if not entry_embedding:
            continue
        similarity = cosine_similarity(
            [query_embedding], [entry_embedding])[0][0]

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = entry

    if best_match:
        return {
            "title": best_match.title,
            "description": capitalize_sentences(best_match.description) if best_match.description else '',
            "url": best_match.url,
            "source": "internal",
            "similarity_score": highest_similarity,
        }
    return None


# Function to get embeddings from OpenAI
def get_embedding(text):
    try:
        response = client.embeddings.create(
            input=text, model="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']
    except Exception as e:
        logging.error(f"OpenAI API error in get_embedding: {e}")
        return None


# Function to perform an online search using SerpAPI
def search_online(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": serpapi_key,
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        search_results = response.json().get("organic_results", [])

        if search_results:
            top_result = search_results[0]
            return {
                "title": top_result.get("title"),
                "description": capitalize_sentences(top_result.get("snippet", "")),
                "url": top_result.get("link"),
                "source": "online",
            }
        else:
            return {"message": "No information found."}
    except Exception as e:
        logging.error(f"Error in search_online: {e}")
        return {"error": "Failed to fetch online results"}


@app.route('/feedback', methods=['POST'])
def feedback():
    feedback_data = request.json.get('feedback')
    if 'memory' in session and session['memory']:
        session['memory'][-1]['feedback'] = feedback_data
    return jsonify({"message": "Feedback recorded. Thank you!"})


@app.route("/", methods=["GET"])
def home():
    return "Server is running!"


# Temporary function to verify spaCy tokenization
@app.route('/test_spacy', methods=['GET'])
def test_spacy():
    try:
        test_text = "This is a test sentence."
        doc = nlp(test_text)
        tokens = [token.text for token in doc]
        return jsonify({"tokens": tokens})
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=5001)