import streamlit as st
from modules.groq_client import ask_groq

def home_page():
    st.title("🤖 General AI Agent")
    st.write("Ask anything!")

    user_input = st.text_area("Your question:")

    if st.button("Ask"):
        if user_input.strip() == "":
            st.warning("Write something first!")
        else:
            answer = ask_groq(user_input)
            st.success(answer)
