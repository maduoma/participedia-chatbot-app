# app/services/preprocess_service.py
import pandas as pd
import os
from app.models import Case, Method
from app import db
from app.data_processing.data_preprocessing import preprocess_case_data, preprocess_method_data

# Paths to save cleaned datasets within the raw_clean_data directory
CLEANED_CASE_PATH = 'data_processing/raw_clean_data/cleaned_case_data.csv'
CLEANED_METHOD_PATH = 'data_processing/raw_clean_data/cleaned_method_data.csv'


def preprocess_case_data(file_path):
    case_data = pd.read_csv(file_path, encoding='utf-8')
    case_data = case_data[['id', 'title', 'description', 'url']]
    case_data.dropna(subset=['title', 'url'], inplace=True)
    case_data['description'] = case_data['description'].fillna('')
    case_data['title'] = case_data['title'].str.lower()
    case_data['description'] = case_data['description'].str.lower()
    case_data.to_csv(CLEANED_CASE_PATH, index=False, encoding='utf-8')
    print(f"Cleaned case data saved to {CLEANED_CASE_PATH}")
    load_data_to_db(case_data, Case)


def preprocess_method_data(file_path):
    method_data = pd.read_csv(file_path, encoding='utf-8')
    method_data = method_data[['id', 'title', 'description', 'url']]
    method_data.dropna(subset=['title', 'url'], inplace=True)
    method_data['description'] = method_data['description'].fillna('')
    method_data['title'] = method_data['title'].str.lower()
    method_data['description'] = method_data['description'].str.lower()
    method_data.to_csv(CLEANED_METHOD_PATH, index=False, encoding='utf-8')
    print(f"Cleaned method data saved to {CLEANED_METHOD_PATH}")
    load_data_to_db(method_data, Method)


def load_data_to_db(data, model):
    for _, row in data.iterrows():
        existing_entry = model.query.filter_by(id=row['id']).first()
        if existing_entry is None:
            new_entry = model(
                id=row['id'],
                title=row['title'],
                description=row['description'],
                url=row['url']
            )
            db.session.add(new_entry)
    db.session.commit()
    print(f"Data loaded into {model.__tablename__} table in the database.")
