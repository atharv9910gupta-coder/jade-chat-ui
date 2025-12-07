import streamlit as st
import json
import os

st.set_page_config(page_title="Admin Dashboard", page_icon="🛠️")

st.title("🛠️ Admin Dashboard")
st.write("Manage memory, logs, settings, and more.")

# Memory file path
MEMORY_FILE = "data/memory.json"

# ----- LOAD MEMORY -----
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"history": []}

# ----- SAVE MEMORY -----
def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Display memory
st.subheader("🧠 Conversation Memory")
memory = load_memory()

if st.button("🔄 Refresh Memory"):
    st.rerun()

st.json(memory)

# Clear memory
if st.button("⚠️ Clear All Memory"):
    save_memory({"history": []})
    st.success("Memory cleared!")
