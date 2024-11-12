# app/services/upload_service.py

import pandas as pd
import logging
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.models import Case, Method
from app.data_processing.data_preprocessing import preprocess_case_data, preprocess_method_data

# Define the paths for storing cleaned data
CLEANED_CASE_PATH = 'data_processing/raw_clean_data/cleaned_case_data.csv'
CLEANED_METHOD_PATH = 'data_processing/raw_clean_data/cleaned_method_data.csv'


def process_uploaded_file(filepath):
    """
    Process an uploaded CSV file by determining its type (case or method),
    cleaning the data, and saving it to the database.
    """
    try:
        # Check file type based on filename
        if "case" in filepath.lower():
            cleaned_data = preprocess_case_data(filepath)
            save_to_database(cleaned_data, Case)
            return f"{filepath} processed and saved as Case data."

        elif "method" in filepath.lower():
            cleaned_data = preprocess_method_data(filepath)
            save_to_database(cleaned_data, Method)
            return f"{filepath} processed and saved as Method data."

        else:
            logging.warning(f"File {filepath} does not match expected types (case or method)")
            return f"File {filepath} is not recognized as a Case or Method data file."
    except Exception as e:
        logging.error(f"Error processing file {filepath}: {e}")
        return f"Error processing file {filepath}: {str(e)}"


def save_to_database(cleaned_data, model):
    """
    Save the cleaned data to the database using the specified SQLAlchemy model.
    """
    try:
        # Clear existing data in the table if required
        db.session.query(model).delete()

        # Load data into database row by row
        for _, row in cleaned_data.iterrows():
            db_entry = model(
                id=int(row['id']),
                title=row['title'],
                description=row['description'],
                url=row['url']
            )
            db.session.add(db_entry)

        # Commit transaction
        db.session.commit()
        logging.info(f"Data successfully loaded into {model.__tablename__} table.")

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error: {e}")
        raise
    except Exception as e:
        logging.error(f"Error saving data to {model.__tablename__} table: {e}")
        raise
