# app/routes/upload_routes.py

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
from app.services.upload_service import process_uploaded_file

# Initialize the blueprint for upload routes
upload_routes = Blueprint('upload_routes', __name__)

# Define allowed extensions for file uploads
ALLOWED_EXTENSIONS = {'csv'}


# Check if uploaded file has a valid extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_routes.route('/upload', methods=['POST'])
def upload_files():
    """
    Endpoint to handle uploading of multiple CSV files.
    """
    if 'files' not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist('files')
    upload_results = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join('data_processing/raw_clean_data', filename)

            try:
                # Save file to the specified path
                file.save(filepath)
                logging.info(f"File {filename} saved successfully at {filepath}")

                # Process the uploaded file (e.g., cleaning, storing into database)
                process_result = process_uploaded_file(filepath)
                upload_results.append({"filename": filename, "status": "Processed", "details": process_result})
            except Exception as e:
                logging.error(f"Error processing file {filename}: {e}")
                upload_results.append({"filename": filename, "status": "Failed", "error": str(e)})
        else:
            upload_results.append({"filename": file.filename, "status": "Invalid file type"})

    return jsonify(upload_results), 200
