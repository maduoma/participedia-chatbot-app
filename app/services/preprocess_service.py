# Path: app/service/preprocess_service.py

import pandas as pd
import os
from app import db
from app.models import Case, Method

# Paths to save cleaned datasets within the raw_clean_data directory
CLEANED_CASE_PATH = 'data_processing/raw_clean_data/cleaned_case_data.csv'
CLEANED_METHOD_PATH = 'data_processing/raw_clean_data/cleaned_method_data.csv'


def preprocess_case_data(file_path):
    """
    Preprocess case data by loading the CSV file, cleaning, and saving it.
    """
    # Load the dataset
    case_data = pd.read_csv(file_path, encoding='utf-8')

    # Select essential columns
    case_data = case_data[['id', 'title', 'description', 'url']]

    # Drop rows with missing titles or URLs
    case_data.dropna(subset=['title', 'url'], inplace=True)

    # Fill missing descriptions with an empty string
    case_data['description'] = case_data['description'].fillna('')

    # Standardize text to lowercase
    case_data['title'] = case_data['title'].str.lower()
    case_data['description'] = case_data['description'].str.lower()

    # Save the cleaned data to the specified path
    case_data.to_csv(CLEANED_CASE_PATH, index=False, encoding='utf-8')
    print(f"Cleaned case data saved to {CLEANED_CASE_PATH}")

    # Load data to the database
    load_data_to_db(case_data, Case)


def preprocess_method_data(file_path):
    """
    Preprocess method data by loading the CSV file, cleaning, and saving it.
    """
    # Load the dataset
    method_data = pd.read_csv(file_path, encoding='utf-8')

    # Select essential columns
    method_data = method_data[['id', 'title', 'description', 'url']]

    # Drop rows with missing titles or URLs
    method_data.dropna(subset=['title', 'url'], inplace=True)

    # Fill missing descriptions with an empty string
    method_data['description'] = method_data['description'].fillna('')

    # Standardize text to lowercase
    method_data['title'] = method_data['title'].str.lower()
    method_data['description'] = method_data['description'].str.lower()

    # Save the cleaned data to the specified path
    method_data.to_csv(CLEANED_METHOD_PATH, index=False, encoding='utf-8')
    print(f"Cleaned method data saved to {CLEANED_METHOD_PATH}")

    # Load data to the database
    load_data_to_db(method_data, Method)


def load_data_to_db(data, model):
    """
    Load cleaned data into the database.
    """
    for _, row in data.iterrows():
        # Check if the entry already exists
        existing_entry = model.query.filter_by(id=row['id']).first()
        if existing_entry is None:
            # Create a new instance of the model and add it to the database session
            new_entry = model(
                id=row['id'],
                title=row['title'],
                description=row['description'],
                url=row['url']
            )
            db.session.add(new_entry)
    db.session.commit()
    print(f"Data loaded into {model.__tablename__} table in the database.")
