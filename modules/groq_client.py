import os
from groq import Groq

def run_groq_chat(prompt):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    chat_completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return chat_completion.choices[0].message["content"]

