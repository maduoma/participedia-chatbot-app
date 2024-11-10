# app/services/search_service.py

from ..models import db, Case, Method
from ..services.openai_service import get_embedding
from ..utils.text_utils import capitalize_sentences
from sklearn.metrics.pairwise import cosine_similarity
import re
import requests
import logging
from config import Config

# Set up SerpAPI key
serpapi_key = Config.SERPAPI_API_KEY

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)


def search_exact_case_method(query):
    """
    Checks if the query contains a specific case or method ID and retrieves the record from the database.
    """
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


def semantic_search(model, query):
    """
    Performs a semantic search by calculating cosine similarity between the query embedding and records.
    """
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
        similarity = cosine_similarity([query_embedding], [entry_embedding])[0][0]

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


def search_online(query):
    """
    Uses SerpAPI to perform an online search if no local results are found.
    """
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
