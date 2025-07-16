import streamlit as st
import requests
import json
import time

# Using a more reliable model
API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

st.set_page_config(
    page_title="🩺 AI Health Assistant", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 30px;
    }
    .disclaimer {
        background-color: #FFF3CD;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FFC107;
        margin-bottom: 20px;
    }
    .symptom-form {
        background-color: #F8F9FA;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .advice-box {
        background-color: #E8F5E8;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #28A745;
    }
    .urgent-box {
        background-color: #F8D7DA;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #DC3545;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🩺 AI Health Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Free, accessible health guidance for underserved communities</p>', unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div class="disclaimer">
    <strong>⚠️ Important Disclaimer:</strong> This tool provides preliminary health guidance only. 
    It is NOT a substitute for professional medical advice, diagnosis, or treatment. 
    Always consult with a qualified healthcare provider for serious symptoms.
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'assessment_stage' not in st.session_state:
    st.session_state.assessment_stage = 'initial'

# Sidebar for user profile
with st.sidebar:
    st.header("👤 User Profile")
    
    age = st.selectbox("Age Group", ["Select", "0-12", "13-17", "18-30", "31-50", "51-65", "65+"])
    gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other", "Prefer not to say"])
    location = st.selectbox("Location Type", ["Select", "Urban", "Rural", "Semi-urban"])
    language = st.selectbox("Preferred Language", ["English", "Hindi", "Spanish", "French", "Arabic"])
    
    if st.button("Save Profile"):
        st.session_state.user_profile = {
            'age': age,
            'gender': gender,
            'location': location,
            'language': language
        }
        st.success("Profile saved!")

# Health assessment questions
def get_health_assessment():
    st.markdown('<div class="symptom-form">', unsafe_allow_html=True)
    st.subheader("🔍 Health Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        main_symptom = st.text_area("What is your main symptom or concern?", height=100)
        duration = st.selectbox("How long have you had this symptom?", 
                               ["Select", "Less than 1 day", "1-3 days", "4-7 days", "1-2 weeks", "More than 2 weeks"])
        severity = st.slider("Rate the severity (1-10)", 1, 10, 5)
    
    with col2:
        other_symptoms = st.multiselect("Any other symptoms?", 
                                      ["Fever", "Headache", "Nausea", "Fatigue", "Cough", "Shortness of breath", 
                                       "Chest pain", "Abdominal pain", "Dizziness", "Skin rash"])
        medical_history = st.text_area("Any relevant medical history?", height=60)
        medications = st.text_area("Current medications?", height=60)
    
    current_condition = st.text_area("Describe your current condition in detail:", height=100)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return {
        'main_symptom': main_symptom,
        'duration': duration,
        'severity': severity,
        'other_symptoms': other_symptoms,
        'medical_history': medical_history,
        'medications': medications,
        'current_condition': current_condition
    }

# Emergency check
def check_emergency_symptoms(symptoms_data):
    emergency_keywords = [
        'chest pain', 'severe headache', 'difficulty breathing', 'shortness of breath',
        'severe abdominal pain', 'high fever', 'bleeding', 'unconscious',
        'severe allergic reaction', 'stroke', 'heart attack', 'seizure'
    ]
    
    text_to_check = f"{symptoms_data['main_symptom']} {symptoms_data['current_condition']}".lower()
    
    for keyword in emergency_keywords:
        if keyword in text_to_check:
            return True
    
    if symptoms_data['severity'] >= 8:
        return True
    
    return False

# Generate health advice based on symptoms
def generate_health_advice(symptoms_data, user_profile):
    advice = []
    
    # Emergency check
    if check_emergency_symptoms(symptoms_data):
        return {
            'type': 'emergency',
            'advice': "⚠️ SEEK IMMEDIATE MEDICAL ATTENTION! Based on your symptoms, you should visit the nearest emergency room or call emergency services immediately."
        }
    
    # Basic advice based on common symptoms
    main_symptom = symptoms_data['main_symptom'].lower()
    
    if 'fever' in main_symptom or 'Fever' in symptoms_data['other_symptoms']:
        advice.append("🌡️ For fever: Rest, stay hydrated, and take paracetamol/acetaminophen as directed.")
    
    if 'headache' in main_symptom or 'Headache' in symptoms_data['other_symptoms']:
        advice.append("🧠 For headache: Rest in a quiet, dark room, apply a cold compress, and stay hydrated.")
    
    if 'cough' in main_symptom or 'Cough' in symptoms_data['other_symptoms']:
        advice.append("🤧 For cough: Stay hydrated, use honey (if over 1 year old), and avoid irritants.")
    
    if 'nausea' in main_symptom or 'Nausea' in symptoms_data['other_symptoms']:
        advice.append("🤢 For nausea: Try ginger tea, eat bland foods (BRAT diet), and avoid strong odors.")
    
    # Duration-based advice
    if symptoms_data['duration'] in ['1-2 weeks', 'More than 2 weeks']:
        advice.append("⏰ Since symptoms have persisted for over a week, consider consulting a healthcare provider.")
    
    # Severity-based advice
    if symptoms_data['severity'] >= 6:
        advice.append("⚠️ Given the severity of your symptoms, it's recommended to consult a healthcare professional.")
    
    # General advice
    advice.extend([
        "💧 Stay well hydrated by drinking plenty of water",
        "🛌 Get adequate rest and sleep",
        "🍲 Eat nutritious, easily digestible foods",
        "🚭 Avoid smoking and alcohol"
    ])
    
    return {
        'type': 'general',
        'advice': advice
    }

# Main interface
def main():
    # Health Assessment Form
    symptoms_data = get_health_assessment()
    
    if st.button("🔍 Get Health Guidance", type="primary"):
        if symptoms_data['main_symptom'] and symptoms_data['duration'] != "Select":
            with st.spinner("🤖 Analyzing your symptoms..."):
                advice_result = generate_health_advice(symptoms_data, st.session_state.user_profile)
                
                if advice_result['type'] == 'emergency':
                    st.markdown(f'<div class="urgent-box">{advice_result["advice"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="advice-box">', unsafe_allow_html=True)
                    st.markdown("**🩺 Health Guidance:**")
                    for advice_item in advice_result['advice']:
                        st.markdown(f"• {advice_item}")
                    
                    st.markdown("**📞 When to seek professional help:**")
                    st.markdown("• If symptoms worsen or don't improve in 2-3 days")
                    st.markdown("• If you develop new concerning symptoms")
                    st.markdown("• If you're unsure about your condition")
                    st.markdown("• If you have underlying health conditions")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Track usage (simplified)
                st.session_state.chat_history.append({
                    'timestamp': time.time(),
                    'symptoms': symptoms_data['main_symptom'],
                    'advice_type': advice_result['type']
                })
        else:
            st.error("Please fill in at least the main symptom and duration.")

# Quick symptom checker
st.markdown("### 🚀 Quick Symptom Checker")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🤒 Cold/Flu Symptoms"):
        st.info("Rest, fluids, and monitor temperature. See a doctor if symptoms worsen or last >10 days.")

with col2:
    if st.button("🤕 Minor Injury"):
        st.info("Clean wound, apply bandage. For serious cuts or persistent pain, seek medical care.")

with col3:
    if st.button("😰 Stress/Anxiety"):
        st.info("Try deep breathing, exercise, or meditation. Consider professional help if persistent.")

# Main assessment
main()

# Statistics (for tracking as mentioned in lean canvas)
if st.sidebar.button("📊 Usage Statistics"):
    st.sidebar.write(f"Total consultations: {len(st.session_state.chat_history)}")
    if st.session_state.user_profile:
        st.sidebar.write(f"User location: {st.session_state.user_profile.get('location', 'Not specified')}")
        st.sidebar.write(f"User age: {st.session_state.user_profile.get('age', 'Not specified')}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🌍 Supporting SDG Goal 3: Good Health and Well-being</p>
    <p>Available in multiple languages • Accessible in low-bandwidth areas • Free for all</p>
    <p>For emergency situations, always call your local emergency number</p>
</div>
""", unsafe_allow_html=True)