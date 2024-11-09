# File: data_preprocessing.py

import pandas as pd

# Paths to the raw datasets
case_dataset_path = 'raw_clean_data/Case Dataset.csv'
method_dataset_path = 'raw_clean_data/Method Dataset.csv'

# Paths to save cleaned datasets
cleaned_case_path = 'raw_clean_data/cleaned_case_data.csv'
cleaned_method_path = 'raw_clean_data/cleaned_method_data.csv'


def preprocess_case_data():
    # Load the case dataset with UTF-8 encoding
    case_data = pd.read_csv(case_dataset_path, encoding='utf-8')

    # Select essential columns
    case_data = case_data[['id', 'title', 'description', 'url']]

    # Drop rows with missing titles or URLs
    case_data = case_data.dropna(subset=['title', 'url'])

    # Fill missing descriptions with an empty string
    case_data['description'] = case_data['description'].fillna('')

    # Standardize text to lowercase and handle encoding issues
    case_data['title'] = case_data['title'].str.lower().apply(lambda x: x.encode('utf-8', 'ignore').decode('utf-8'))
    case_data['description'] = case_data['description'].str.lower().apply(
        lambda x: x.encode('utf-8', 'ignore').decode('utf-8'))

    # Save cleaned data
    case_data.to_csv(cleaned_case_path, index=False, encoding='utf-8')
    print(f"Cleaned case data saved to {cleaned_case_path}")


def preprocess_method_data():
    # Load the method dataset with UTF-8 encoding
    method_data = pd.read_csv(method_dataset_path, encoding='utf-8')

    # Select essential columns
    method_data = method_data[['id', 'title', 'description', 'url']]

    # Drop rows with missing titles or URLs
    method_data = method_data.dropna(subset=['title', 'url'])

    # Fill missing descriptions with an empty string
    method_data['description'] = method_data['description'].fillna('')

    # Standardize text to lowercase and handle encoding issues
    method_data['title'] = method_data['title'].str.lower().apply(lambda x: x.encode('utf-8', 'ignore').decode('utf-8'))
    method_data['description'] = method_data['description'].str.lower().apply(
        lambda x: x.encode('utf-8', 'ignore').decode('utf-8'))

    # Save cleaned data
    method_data.to_csv(cleaned_method_path, index=False, encoding='utf-8')
    print(f"Cleaned method data saved to {cleaned_method_path}")


if __name__ == "__main__":
    preprocess_case_data()
    preprocess_method_data()
