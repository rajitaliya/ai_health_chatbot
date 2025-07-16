import streamlit as st
import requests

# ✅ CORRECT Model name
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"

st.set_page_config(page_title="🩺 AI Health Chatbot", layout="centered")
st.title("🩺 AI Health Chatbot")

hf_token = st.text_input("🔐 Enter your Hugging Face Token", type="password")

def ask_bot(symptoms, token):
    headers = {"Authorization": f"Bearer {token}"}
    prompt = f"Give basic health advice for the following symptoms:\n{symptoms}"
    res = requests.post(API_URL, headers=headers, json={"inputs": prompt})

    if res.status_code == 200:
        try:
            return res.json()[0]['generated_text']
        except Exception:
            return "⚠️ Could not parse response."
    elif res.status_code == 403:
        return "❌ Token unauthorized. Make sure it has 'Inference Providers' permission."
    elif res.status_code == 404:
        return "❌ Model not found. Please double-check the model name in code."
    elif res.status_code == 401:
        return "❌ Invalid token. Please regenerate your Hugging Face token."
    else:
        return f"⚠️ Unexpected error: {res.status_code} - {res.text}"

if hf_token:
    user_input = st.chat_input("Describe your symptoms here...")
    if user_input:
        with st.spinner("🤖 Thinking..."):
            result = ask_bot(user_input, hf_token)
        st.markdown(f"**🩺 AI Response:** {result}")
else:
    st.info("Please enter a valid Hugging Face token to start chatting.")
