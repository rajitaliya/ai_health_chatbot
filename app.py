import streamlit as st
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

st.set_page_config(page_title="🩺 Health Assistant", layout="centered")

# Get Groq API key
if "GROQ_API_KEY" not in st.session_state:
    st.session_state.GROQ_API_KEY = ""

if not st.session_state.GROQ_API_KEY:
    st.session_state.GROQ_API_KEY = st.text_input("Enter Groq API Key:", type="password")

def get_health_advice(condition, api_key):
    """Get health advice using LangChain's ChatGroq"""
    try:
        llm = ChatGroq(
            model="llama-3.1-8b-instant",   # ✅ free Groq model
            temperature=0.7,
            groq_api_key=api_key
        )

        response = llm.invoke([
            {
                "role": "system",
                "content": "You are a helpful medical assistant. Provide brief, practical health advice for common conditions. Always remind users to consult healthcare professionals for serious concerns. Keep responses concise and helpful."
            },
            {
                "role": "user",
                "content": f"I have {condition}. What should I do?"
            }
        ])
        return response.content
    except Exception as e:
        return f"Error getting advice: {str(e)}"

# Main Interface
st.title("🩺 Health Assistant")
st.write("Simple health guidance powered by AI (Groq)")

st.warning("⚠️ This provides general guidance only. Consult healthcare professionals for proper diagnosis.")

# Simple input form
with st.form("health_form"):
    condition_input = st.text_area(
        "Describe your health condition or symptoms:",
        placeholder="e.g., I have a headache and feel tired, or I have been coughing for 3 days"
    )

    submitted = st.form_submit_button("Get Health Advice")

    if submitted and condition_input:
        if st.session_state.GROQ_API_KEY:
            with st.spinner("🤖 Getting health advice..."):
                advice = get_health_advice(condition_input, st.session_state.GROQ_API_KEY)
                st.success("**AI Health Advice:**")
                st.write(advice)
        else:
            st.error("Please enter your Groq API key first.")
    elif submitted:
        st.error("Please describe your condition.")

# Emergency notice
st.subheader("🚨 Emergency")
st.error("For medical emergencies, call: 102 (India) | 911 (USA) | 999 (UK)")

st.markdown("---")
st.write("🤖 Powered by Groq • 🌍 Free Health Guidance")
