import pandas as pd
from sqlalchemy import create_engine, text
import os

# PostgreSQL connection URL
DATABASE_URI = 'postgresql://postgres:postgres@localhost/chatbot_db?client_encoding=utf8'

# Paths to cleaned data
CLEANED_CASE_PATH = 'raw_clean_data/cleaned_case_data.csv'
CLEANED_METHOD_PATH = 'raw_clean_data/cleaned_method_data.csv'

# Initialize PostgreSQL engine
engine = create_engine(DATABASE_URI)


def setup_database():
    with engine.connect() as conn:
        # Ensure UTF-8 encoding for this connection
        conn.execute(text("SET client_encoding TO 'UTF8'"))

        # Drop tables if they exist
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

        # Create 'chat_sessions' table
        conn.execute(text("""
            CREATE TABLE chat_sessions (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR NOT NULL,
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
    if not os.path.exists(CLEANED_CASE_PATH):
        print(f"{CLEANED_CASE_PATH} does not exist.")
        return
    if not os.path.exists(CLEANED_METHOD_PATH):
        print(f"{CLEANED_METHOD_PATH} does not exist.")
        return

    case_data = pd.read_csv(CLEANED_CASE_PATH, encoding='utf-8')
    method_data = pd.read_csv(CLEANED_METHOD_PATH, encoding='utf-8')

    # Use a database session for transaction management
    with engine.begin() as connection:
        # Acquire an exclusive lock on the cases and methods tables
        connection.execute(text("LOCK TABLE cases IN ACCESS EXCLUSIVE MODE"))
        connection.execute(text("LOCK TABLE methods IN ACCESS EXCLUSIVE MODE"))

        # Clear existing data in cases and methods tables
        connection.execute(text("DELETE FROM cases"))
        connection.execute(text("DELETE FROM methods"))

        # Load data into PostgreSQL tables
        case_data.to_sql('cases', connection, if_exists='append', index=False)
        method_data.to_sql('methods', connection, if_exists='append', index=False)

    print("Cleaned data loaded into PostgreSQL database.")


if __name__ == "__main__":
    setup_database()
    load_data_to_db()
