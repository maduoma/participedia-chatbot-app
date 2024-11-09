# File: app.py

from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import openai
import requests
import re
import os
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import numpy as np

# Load configuration
from config import Config

# Initialize Flask app and configure database
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY  # For session management
db = SQLAlchemy(app)

# Set up OpenAI and SerpAPI keys
openai.api_key = Config.OPENAI_API_KEY
serpapi_key = Config.SERPAPI_API_KEY

# Initialize NLP tools
lemmatizer = WordNetLemmatizer()


# SQLAlchemy Models for Cases and Methods
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


# Endpoint to handle user queries
@app.route('/query', methods=['POST'])
def handle_query():
    user_query = request.json.get('query')

    # Preprocess the query
    processed_query = preprocess_query(user_query)

    # Step 1: Use OpenAI API for NLP-based intent classification
    intent = classify_query(processed_query)

    # Step 2: Check for specific case/method match
    result = search_exact_case_method(processed_query)

    # Step 3: If no exact match, perform semantic search based on intent
    if not result:
        if intent == "case":
            result = semantic_search(Case, processed_query)
        elif intent == "method":
            result = semantic_search(Method, processed_query)
        else:
            result = None

    # Step 4: Fallback to online search if no result
    if not result:
        result = search_online(processed_query)

    # Step 5: Add response to session memory
    if 'memory' not in session:
        session['memory'] = []
    session['memory'].append({"query": user_query, "response": result})

    return jsonify(result)


def preprocess_query(query):
    # Tokenize, lemmatize, and lower-case the query for standardization
    tokens = word_tokenize(query.lower())
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return " ".join(lemmatized_tokens)


def classify_query(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Classify the user query into either 'case', 'method', or 'general'."},
                {"role": "user", "content": query}
            ]
        )
        intent = response['choices'][0]['message']['content'].strip().lower()
        return intent
    except Exception as e:
        print("OpenAI API error:", e)
        return "general"


def search_exact_case_method(query):
    case_match = re.search(r'\bcase\s+(\d+)\b', query, re.IGNORECASE)
    method_match = re.search(r'\bmethod\s+(\d+)\b', query, re.IGNORECASE)

    if case_match:
        case_id = int(case_match.group(1))
        result = Case.query.get(case_id)
        if result:
            return {
                "title": result.title,
                "description": result.description,
                "url": result.url,
                "source": "internal"
            }

    if method_match:
        method_id = int(method_match.group(1))
        result = Method.query.get(method_id)
        if result:
            return {
                "title": result.title,
                "description": result.description,
                "url": result.url,
                "source": "internal"
            }

    return None


def semantic_search(model, query):
    entries = model.query.all()
    query_embedding = get_embedding(query)

    best_match = None
    highest_similarity = -1

    for entry in entries:
        entry_text = f"{entry.title} {entry.description}"
        entry_embedding = get_embedding(entry_text)
        similarity = cosine_similarity([query_embedding], [entry_embedding])[0][0]

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = entry

    if best_match:
        return {
            "title": best_match.title,
            "description": best_match.description,
            "url": best_match.url,
            "source": "internal",
            "similarity_score": highest_similarity
        }
    return None


def get_embedding(text):
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    return response['data'][0]['embedding']


def search_online(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": serpapi_key
    }
    response = requests.get("https://serpapi.com/search", params=params)
    search_results = response.json().get("organic_results", [])

    if search_results:
        top_result = search_results[0]
        return {
            "title": top_result.get("title"),
            "description": top_result.get("snippet"),
            "url": top_result.get("link"),
            "source": "online"
        }
    else:
        return {"message": "No information found."}


@app.route('/feedback', methods=['POST'])
def feedback():
    feedback_data = request.json.get('feedback')
    if 'memory' in session:
        session['memory'][-1]['feedback'] = feedback_data
    return jsonify({"message": "Feedback recorded. Thank you!"})


@app.route("/", methods=["GET"])
def home():
    return "Server is running!"


if __name__ == '__main__':
    app.run(debug=True, port=5001)

# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import or_
# import openai
# import requests
# import re
# import os

# # Load configuration
# from config import Config

# # Initialize Flask app and configure database
# app = Flask(__name__)
# app.config.from_object(Config)
# db = SQLAlchemy(app)

# # Set up OpenAI and SerpAPI keys
# openai.api_key = Config.OPENAI_API_KEY
# serpapi_key = Config.SERPAPI_API_KEY

# # SQLAlchemy Models for Cases and Methods
# class Case(db.Model):
#     __tablename__ = 'cases'
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String, nullable=False)
#     description = db.Column(db.Text, nullable=True)
#     url = db.Column(db.String, nullable=True)

# class Method(db.Model):
#     __tablename__ = 'methods'
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String, nullable=False)
#     description = db.Column(db.Text, nullable=True)
#     url = db.Column(db.String, nullable=True)

# # Endpoint to handle user queries
# @app.route('/query', methods=['POST'])
# def handle_query():
#     user_query = request.json.get('query')

#     # Step 1: Use OpenAI API for NLP-based intent classification
#     intent = classify_query(user_query)

#     # Step 2: Prioritize exact case/method match
#     result = search_exact_case_method(user_query)

#     # Step 3: If no exact match, perform broader search based on intent
#     if not result:
#         if intent == "case":
#             result = search_database(Case, user_query)
#         elif intent == "method":
#             result = search_database(Method, user_query)
#         else:
#             result = None

#     # Step 4: If no local result, use SerpAPI for online search
#     if not result:
#         result = search_online(user_query)

#     return jsonify(result)

# def classify_query(query):
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "Classify the user query into either 'case', 'method', or 'general'."},
#                 {"role": "user", "content": query}
#             ]
#         )
#         # Extract the classification from the response
#         intent = response['choices'][0]['message']['content'].strip().lower()
#         return intent
#     except Exception as e:
#         print("OpenAI API error:", e)
#         return "general"  # Default to 'general' if there's an error

# def search_exact_case_method(query):
#     # Check for exact case/method reference in query using regex
#     case_match = re.search(r'\bcase\s+(\d+)\b', query, re.IGNORECASE)
#     method_match = re.search(r'\bmethod\s+(\d+)\b', query, re.IGNORECASE)

#     if case_match:
#         case_id = int(case_match.group(1))
#         result = Case.query.get(case_id)
#         if result:
#             return {
#                 "title": result.title,
#                 "description": result.description,
#                 "url": result.url,
#                 "source": "internal"
#             }

#     if method_match:
#         method_id = int(method_match.group(1))
#         result = Method.query.get(method_id)
#         if result:
#             return {
#                 "title": result.title,
#                 "description": result.description,
#                 "url": result.url,
#                 "source": "internal"
#             }

#     return None  # No exact match found

# def search_database(model, query):
#     # Perform a broader search in the title and description columns if no exact match
#     result = model.query.filter(
#         or_(model.title.ilike(f"%{query}%"), model.description.ilike(f"%{query}%"))
#     ).first()

#     if result:
#         return {
#             "title": result.title,
#             "description": result.description,
#             "url": result.url,
#             "source": "internal"
#         }
#     return None

# def search_online(query):
#     # Fallback search using SerpAPI
#     params = {
#         "engine": "google",
#         "q": query,
#         "api_key": serpapi_key
#     }
#     response = requests.get("https://serpapi.com/search", params=params)
#     search_results = response.json().get("organic_results", [])

#     if search_results:
#         # Take the first result from SerpAPI
#         top_result = search_results[0]
#         return {
#             "title": top_result.get("title"),
#             "description": top_result.get("snippet"),
#             "url": top_result.get("link"),
#             "source": "online"
#         }
#     else:
#         return {"message": "No information found."}

# # Simple route to confirm the server is running
# @app.route("/", methods=["GET"])
# def home():
#     return "Server is running!"

# if __name__ == '__main__':
#     app.run(debug=True, port=5001)  # Replace 5001 with an available port if needed
