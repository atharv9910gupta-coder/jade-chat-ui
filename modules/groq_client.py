import os
from groq import Groq

def run_groq_chat(messages):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    return completion.choices[0].message["content"]
