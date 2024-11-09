# File: db_setup.py

import pandas as pd
from sqlalchemy import create_engine, text

# PostgreSQL connection URL
DATABASE_URI = 'postgresql://postgres:postgres@localhost/chatbot_db?client_encoding=utf8'

# Paths to cleaned data
cleaned_case_path = 'raw_clean_data/cleaned_case_data.csv'
cleaned_method_path = 'raw_clean_data/cleaned_method_data.csv'

# Initialize PostgreSQL engine
engine = create_engine(DATABASE_URI)

def setup_database():
    with engine.connect() as conn:
        # Ensure UTF-8 encoding for this connection
        conn.execute(text("SET client_encoding TO 'UTF8'"))

        # Drop tables if they exist
        conn.execute(text("DROP TABLE IF EXISTS cases"))
        conn.execute(text("DROP TABLE IF EXISTS methods"))

        # Create 'cases' table
        conn.execute(text("""
            CREATE TABLE cases (
                id INTEGER PRIMARY KEY,
                title VARCHAR NOT NULL,
                description TEXT,
                url VARCHAR NOT NULL
            )
        """))

        # Create 'methods' table
        conn.execute(text("""
            CREATE TABLE methods (
                id INTEGER PRIMARY KEY,
                title VARCHAR NOT NULL,
                description TEXT,
                url VARCHAR NOT NULL
            )
        """))

        # Create indexes on 'title' and 'description' for both tables for faster search
        conn.execute(text("CREATE INDEX idx_cases_title ON cases (title)"))
        conn.execute(text("CREATE INDEX idx_cases_description ON cases (description)"))
        conn.execute(text("CREATE INDEX idx_methods_title ON methods (title)"))
        conn.execute(text("CREATE INDEX idx_methods_description ON methods (description)"))

        print("Database tables and indexes created successfully.")

def load_data_to_db():
    # Load cleaned datasets
    case_data = pd.read_csv(cleaned_case_path, encoding='utf-8')
    method_data = pd.read_csv(cleaned_method_path, encoding='utf-8')

    # Load data into PostgreSQL tables
    case_data.to_sql('cases', engine, if_exists='append', index=False)
    method_data.to_sql('methods', engine, if_exists='append', index=False)

    print("Cleaned data loaded into PostgreSQL database.")

if __name__ == "__main__":
    setup_database()
    load_data_to_db()