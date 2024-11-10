# classification_utils.py

def is_greeting(query):
    greetings = ["hi", "hello", "hey", "greetings", "good morning", "good evening"]
    return any(greeting in query.lower() for greeting in greetings)


def classify_query(query, openai_client):
    response = openai_client.Completion.create(
        model="gpt-3.5-turbo",
        prompt=f"Classify this query: '{query}' as either 'case', 'method', or 'general'.",
        max_tokens=10
    )
    return response.choices[0].text.strip().lower()
