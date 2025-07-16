import streamlit as st
import requests

API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-rw-1b"

st.set_page_config(page_title="🩺 AI Health Chatbot", layout="centered")
st.title("🩺 AI Health Chatbot")

hf_token = st.text_input("🔐 Enter your Hugging Face Token", type="password")

def query(payload, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            return response.json()[0]["generated_text"]
        except Exception:
            return "⚠️ Could not parse response."
    elif response.status_code == 403:
        return "❌ Unauthorized token. Check permission: 'Inference Providers'"
    elif response.status_code == 404:
        return "❌ Model not found. Double-check model name."
    elif response.status_code == 401:
        return "❌ Invalid token. Please regenerate it."
    else:
        return f"⚠️ Error {response.status_code}: {response.text}"

if hf_token:
    user_input = st.chat_input("Type your symptoms here...")
    if user_input:
        with st.spinner("🤖 Thinking..."):
            result = query({"inputs": f"Give health advice for: {user_input}"}, hf_token)
        st.markdown(f"**🩺 AI Response:** {result}")
else:
    st.info("Please enter a valid Hugging Face token to begin.")
