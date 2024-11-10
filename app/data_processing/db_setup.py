# Path: app/data_processing/db_setup.py

import pandas as pd
from sqlalchemy import create_engine, text
from config import Config

# Database connection URI from the configuration file
DATABASE_URI = Config.SQLALCHEMY_DATABASE_URI

# Paths to cleaned data files
cleaned_case_path = 'data_processing/raw_clean_data/cleaned_case_data.csv'
cleaned_method_path = 'data_processing/raw_clean_data/cleaned_method_data.csv'

# Initialize the database engine
engine = create_engine(DATABASE_URI)


def setup_database():
    """
    Function to create the required tables in the database with specified schema.
    It will drop the tables if they already exist and create new ones.
    """
    with engine.connect() as conn:
        # Set UTF-8 encoding for the connection
        conn.execute(text("SET client_encoding TO 'UTF8'"))

        # Drop existing tables if they exist
        conn.execute(text("DROP TABLE IF EXISTS cases"))
        conn.execute(text("DROP TABLE IF EXISTS methods"))

        # Create 'cases' table
        conn.execute(text("""
            CREATE TABLE cases (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                url VARCHAR(255) NOT NULL
            )
        """))

        # Create 'methods' table
        conn.execute(text("""
            CREATE TABLE methods (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                url VARCHAR(255) NOT NULL
            )
        """))

        # Create indexes on 'title' and 'description' for both tables to speed up searches
        conn.execute(text("CREATE INDEX idx_cases_title ON cases (title)"))
        conn.execute(text("CREATE INDEX idx_cases_description ON cases (description)"))
        conn.execute(text("CREATE INDEX idx_methods_title ON methods (title)"))
        conn.execute(text("CREATE INDEX idx_methods_description ON methods (description)"))

        print("Database tables and indexes created successfully.")


def load_data_to_db():
    """
    Function to load cleaned data from CSV files into the database tables.
    """
    # Load cleaned case data
    case_data = pd.read_csv(cleaned_case_path, encoding='utf-8')
    method_data = pd.read_csv(cleaned_method_path, encoding='utf-8')

    # Insert data into respective tables
    case_data.to_sql('cases', engine, if_exists='append', index=False)
    method_data.to_sql('methods', engine, if_exists='append', index=False)

    print("Cleaned data loaded into PostgreSQL database successfully.")


if __name__ == "__main__":
    setup_database()
    load_data_to_db()
