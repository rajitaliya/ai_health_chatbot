import streamlit as st
import requests

#  Supported public model on Hugging Face
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-small"

st.set_page_config(page_title="🩺 AI Health Chatbot")
st.title("🩺 AI Health Chatbot (Fast, Lightweight)")

st.markdown("Enter your Hugging Face API token (with inference permission) to start using the bot.")

#  Ask user for HF Token
hf_token = st.text_input("Enter your Hugging Face Token", type="password")

# Store conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat function
def ask_healthbot(user_input, token):
    headers = {"Authorization": f"Bearer {token}"}
    prompt = f"Give basic health advice for the following symptoms:\n{user_input}"

    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        output = response.json()
        return output[0]["generated_text"]
    elif response.status_code == 403:
        return "❌ Invalid or unauthorized token. Please check your Hugging Face token."
    elif response.status_code == 404:
        return "❌ Model not found. Please verify the model URL or try a supported model."
    else:
        return f"⚠️ Error: {response.status_code} - {response.text}"

# UI flow
if hf_token:
    user_input = st.chat_input("Describe your symptoms here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").markdown(user_input)

        with st.spinner("Asking the health AI..."):
            reply = ask_healthbot(user_input, hf_token)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").markdown(reply)
else:
    st.warning("Please enter your Hugging Face token to begin.")
