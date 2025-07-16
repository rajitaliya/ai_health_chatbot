import streamlit as st
import requests

# Streamlit app config
st.set_page_config(page_title="🩺 AI Health Chatbot", layout="centered")
st.title("🩺 AI-Powered Health Chatbot")
st.markdown("Enter your Hugging Face token and describe your symptoms to get basic health advice.")

# 🔐 User input for Hugging Face Token
hf_token = st.text_input("🔐 Enter your Hugging Face API Token", type="password")

# Chat state
if "messages" not in st.session_state:
    st.session_state.messages = []

# AI Chat Function
def ask_healthbot(user_input, token):
    API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"
    headers = {"Authorization": f"Bearer {token}"}

    prompt = f"""
You are a helpful health assistant. The user describes their symptoms in casual language.
You respond with safe advice based on the symptoms.

USER: {user_input}
AI:"""

    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        output = response.json()
        return output[0]["generated_text"].split("AI:")[-1].strip()
    else:
        return f"⚠️ Error: {response.status_code} - {response.text}"

# Chat interface
if hf_token:
    user_input = st.chat_input("Type your symptoms here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)

        with st.spinner("Asking AI..."):
            reply = ask_healthbot(user_input, hf_token)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").markdown(reply)
else:
    st.warning("Please enter your Hugging Face API token to start chatting.")
