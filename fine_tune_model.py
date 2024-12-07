import pandas as pd
from sqlalchemy import create_engine

DATABASE_URI = 'postgresql://postgres:postgres@localhost/chatbot_db'

def export_for_finetuning():
    # Connect to the database
    engine = create_engine(DATABASE_URI)
    query = """
    SELECT 'What is ' || title || '?' as prompt,
           description as completion
    FROM cases
    UNION ALL
    SELECT 'Explain ' || title || '.' as prompt,
           description as completion
    FROM methods;
    """
    df = pd.read_sql(query, engine)

    # Format for fine-tuning
    df['prompt'] = df['prompt'].str.strip() + " ->"
    df['completion'] = " " + df['completion'].str.strip()

    # Save to JSONL
    df.to_json("fine_tuning_data.jsonl", orient="records", lines=True)
    print("Data exported for fine-tuning.")
