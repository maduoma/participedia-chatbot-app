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
    # Use engine.begin() to ensure transaction is committed
    with engine.begin() as conn:
        # Ensure UTF-8 encoding for this connection
        conn.execute(text("SET client_encoding TO 'UTF8'"))

        # Drop tables if they exist
        conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
        conn.execute(text("DROP TABLE IF EXISTS chat_histories"))
        conn.execute(text("DROP TABLE IF EXISTS chat_sessions"))
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

        # Create 'chat_sessions' table with a 'title' column
        conn.execute(text("""
            CREATE TABLE chat_sessions (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                title VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create 'chat_histories' table
        conn.execute(text("""
            CREATE TABLE chat_histories (
                id SERIAL PRIMARY KEY,
                session_id INTEGER REFERENCES chat_sessions(id) ON DELETE CASCADE,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create indexes for faster search
        conn.execute(text("CREATE INDEX idx_cases_title ON cases (title)"))
        conn.execute(text("CREATE INDEX idx_cases_description ON cases (description)"))
        conn.execute(text("CREATE INDEX idx_methods_title ON methods (title)"))
        conn.execute(text("CREATE INDEX idx_methods_description ON methods (description)"))
        conn.execute(text("CREATE INDEX idx_chat_sessions_user_id ON chat_sessions (user_id)"))
        conn.execute(text("CREATE INDEX idx_chat_histories_session_id ON chat_histories (session_id)"))

        print("Database tables and indexes created successfully.")


def load_data_to_db():
    # Load cleaned datasets
    case_data = pd.read_csv(cleaned_case_path, encoding='utf-8')
    method_data = pd.read_csv(cleaned_method_path, encoding='utf-8')

    # Check for duplicate IDs in case_data
    if case_data['id'].duplicated().any():
        print("Duplicate IDs found in case data. Removing duplicates.")
        case_data = case_data.drop_duplicates(subset=['id'])

    # Check for duplicate IDs in method_data
    if method_data['id'].duplicated().any():
        print("Duplicate IDs found in method data. Removing duplicates.")
        method_data = method_data.drop_duplicates(subset=['id'])

    # Load data into PostgreSQL tables
    case_data.to_sql('cases', engine, if_exists='append', index=False)
    method_data.to_sql('methods', engine, if_exists='append', index=False)

    print("Cleaned data loaded into PostgreSQL database.")


if __name__ == "__main__":
    setup_database()
    load_data_to_db()
