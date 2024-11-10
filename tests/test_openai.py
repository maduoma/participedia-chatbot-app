# test_openai.py

import openai

# Initialize the OpenAI client
client = openai.OpenAI(api_key='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')

try:
    # Create a chat completion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Hello, world!"}
        ]
    )
    print("OpenAI API call successful!")
    print(response)
except Exception as e:
    print("Error calling OpenAI API:", e)
