import streamlit as st
import requests

# ✅ Public API-compatible model
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"

st.set_page_config(page_title="🩺 AI Health Chatbot", layout="centered")
st.title("🩺 AI Health Chatbot (FAST + FREE)")

# Token input
hf_token = st.text_input("🔐 Enter your Hugging Face Token (with inference access)", type="password")

def ask_bot(symptoms, token):
    headers = {"Authorization": f"Bearer {token}"}
    prompt = f"Give basic health advice for the following symptoms:\n{symptoms}"
    res = requests.post(API_URL, headers=headers, json={"inputs": prompt})

    try:
        if res.status_code == 200:
            return res.json()[0]['generated_text']
        elif res.status_code == 403:
            return "❌ Invalid or unauthorized token. Please check your Hugging Face token."
        elif res.status_code == 404:
            return "❌ Model not found. Try another model (e.g., google/flan-t5-small)."
        else:
            return f"⚠️ Error {res.status_code}: {res.text}"
    except Exception as e:
        return f"💥 Unexpected error: {e}"

if hf_token:
    user_input = st.chat_input("Describe your symptoms...")
    if user_input:
        with st.spinner("🤖 Generating advice..."):
            output = ask_bot(user_input, hf_token)
        st.markdown(f"**🩺 AI Response:** {output}")
else:
    st.info("Please enter your Hugging Face token above to use the AI.")
