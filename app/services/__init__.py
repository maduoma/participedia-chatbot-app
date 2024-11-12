# app/services/__init__.py

# Importing the core services for the application
from .openai_service import classify_query, get_embedding
from .search_service import search_exact_case_method, semantic_search, search_online
from .preprocess_service import preprocess_case_data, preprocess_method_data
# from .upload_service import handle_file_upload

# __all__ defines the public API of this package, allowing only the specified items to be imported
# when using "from services import *"
__all__ = [
    "classify_query",
    "get_embedding",
    "search_exact_case_method",
    "semantic_search",
    "search_online",
    "preprocess_case_data",
    "preprocess_method_data",
    # "handle_file_upload",
]