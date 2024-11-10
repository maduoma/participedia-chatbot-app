# app/routes/feedback_routes.py

from flask import Blueprint, request, jsonify, session
from ..models import db, ChatHistory

# Define the blueprint for feedback routes
bp = Blueprint('feedback_routes', __name__)


@bp.route('/feedback', methods=['POST'])
def feedback():
    feedback_data = request.json.get('feedback')

    # Check if there is an active session with chat history
    if 'session_id' in session:
        # Retrieve the latest chat history record for the current session
        chat_history = ChatHistory.query.filter_by(
            session_id=session['session_id']
        ).order_by(ChatHistory.timestamp.desc()).first()

        if chat_history:
            # Add feedback to the chat history record
            chat_history.feedback = feedback_data
            db.session.commit()
            return jsonify({"message": "Feedback recorded. Thank you!"})

    return jsonify({"error": "No active chat session found to attach feedback."}), 400
