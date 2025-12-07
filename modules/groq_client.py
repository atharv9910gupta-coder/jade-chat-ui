import streamlit as st
from groq import Groq


# Create a Groq client using the secret key stored in Streamlit Cloud
def get_groq_client():
    """
    Returns a Groq client instance using the API key stored in Streamlit secrets.
    This keeps your API key SAFE and hidden.
    """
    api_key = st.secrets["GROQ_API_KEY"]  # <-- reads the key securely

    client = Groq(api_key=api_key)
    return client


# Function to generate a chat completion
def generate_chat_completion(messages, model="llama-3.1-8b-instant"):
    """
    Sends the conversation messages to Groq's API and receives the model's reply.
    """
    client = get_groq_client()

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message["content"]

