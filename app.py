import streamlit as st
import time

st.set_page_config(
    page_title="AI Health Assistant", 
    layout="centered"
)

st.title("🩺 AI Health Assistant")
st.write("Free, accessible health guidance for underserved communities")

# Disclaimer
st.warning("⚠️ Important: This tool provides preliminary health guidance only. It is NOT a substitute for professional medical advice. Always consult with a qualified healthcare provider for serious symptoms.")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}

# Sidebar for user profile
with st.sidebar:
    st.header("👤 User Profile")
    
    age = st.selectbox("Age Group", ["Select", "0-12", "13-17", "18-30", "31-50", "51-65", "65+"], key="age_select")
    gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other", "Prefer not to say"], key="gender_select")
    location = st.selectbox("Location Type", ["Select", "Urban", "Rural", "Semi-urban"], key="location_select")
    language = st.selectbox("Preferred Language", ["English", "Hindi", "Spanish", "French", "Arabic"], key="language_select")
    
    if st.button("Save Profile", key="save_profile"):
        st.session_state.user_profile = {
            'age': age,
            'gender': gender,
            'location': location,
            'language': language
        }
        st.success("Profile saved!")

# Emergency check function
def check_emergency_symptoms(main_symptom, other_symptoms, severity, current_condition):
    emergency_keywords = [
        'chest pain', 'severe headache', 'difficulty breathing', 'shortness of breath',
        'severe abdominal pain', 'high fever', 'bleeding', 'unconscious',
        'severe allergic reaction', 'stroke', 'heart attack', 'seizure'
    ]
    
    text_to_check = f"{main_symptom} {current_condition}".lower()
    
    for keyword in emergency_keywords:
        if keyword in text_to_check:
            return True
    
    if severity >= 8:
        return True
    
    return False

# Generate health advice
def generate_health_advice(main_symptom, other_symptoms, duration, severity, medical_history, medications, current_condition):
    advice = []
    
    # Emergency check
    if check_emergency_symptoms(main_symptom, other_symptoms, severity, current_condition):
        return {
            'type': 'emergency',
            'advice': "⚠️ SEEK IMMEDIATE MEDICAL ATTENTION! Based on your symptoms, you should visit the nearest emergency room or call emergency services immediately."
        }
    
    # Basic advice based on common symptoms
    main_symptom_lower = main_symptom.lower()
    
    if 'fever' in main_symptom_lower or 'Fever' in other_symptoms:
        advice.append("🌡️ For fever: Rest, stay hydrated, and take paracetamol/acetaminophen as directed.")
    
    if 'headache' in main_symptom_lower or 'Headache' in other_symptoms:
        advice.append("🧠 For headache: Rest in a quiet, dark room, apply a cold compress, and stay hydrated.")
    
    if 'cough' in main_symptom_lower or 'Cough' in other_symptoms:
        advice.append("🤧 For cough: Stay hydrated, use honey (if over 1 year old), and avoid irritants.")
    
    if 'nausea' in main_symptom_lower or 'Nausea' in other_symptoms:
        advice.append("🤢 For nausea: Try ginger tea, eat bland foods (BRAT diet), and avoid strong odors.")
    
    if 'fatigue' in main_symptom_lower or 'Fatigue' in other_symptoms:
        advice.append("😴 For fatigue: Ensure adequate sleep, eat nutritious meals, and consider light exercise.")
    
    # Duration-based advice
    if duration in ['1-2 weeks', 'More than 2 weeks']:
        advice.append("⏰ Since symptoms have persisted for over a week, consider consulting a healthcare provider.")
    
    # Severity-based advice
    if severity >= 6:
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

# Main health assessment
st.subheader("🔍 Health Assessment")

# Create two columns for better layout
col1, col2 = st.columns(2)

with col1:
    main_symptom = st.text_area("What is your main symptom or concern?", height=100, key="main_symptom")
    duration = st.selectbox("How long have you had this symptom?", 
                           ["Select", "Less than 1 day", "1-3 days", "4-7 days", "1-2 weeks", "More than 2 weeks"], 
                           key="duration")
    severity = st.slider("Rate the severity (1-10)", 1, 10, 5, key="severity")

with col2:
    other_symptoms = st.multiselect("Any other symptoms?", 
                                  ["Fever", "Headache", "Nausea", "Fatigue", "Cough", "Shortness of breath", 
                                   "Chest pain", "Abdominal pain", "Dizziness", "Skin rash"], 
                                  key="other_symptoms")
    medical_history = st.text_area("Any relevant medical history?", height=60, key="medical_history")
    medications = st.text_area("Current medications?", height=60, key="medications")

current_condition = st.text_area("Describe your current condition in detail:", height=100, key="current_condition")

# Get health guidance button
if st.button("🔍 Get Health Guidance", type="primary", key="get_guidance"):
    if main_symptom and duration != "Select":
        with st.spinner("🤖 Analyzing your symptoms..."):
            advice_result = generate_health_advice(main_symptom, other_symptoms, duration, severity, medical_history, medications, current_condition)
            
            if advice_result['type'] == 'emergency':
                st.error(advice_result['advice'])
            else:
                st.success("🩺 Health Guidance:")
                for advice_item in advice_result['advice']:
                    st.write(f"• {advice_item}")
                
                st.info("📞 When to seek professional help:")
                st.write("• If symptoms worsen or don't improve in 2-3 days")
                st.write("• If you develop new concerning symptoms")
                st.write("• If you're unsure about your condition")
                st.write("• If you have underlying health conditions")
            
            # Track usage
            st.session_state.chat_history.append({
                'timestamp': time.time(),
                'symptoms': main_symptom,
                'advice_type': advice_result['type']
            })
    else:
        st.error("Please fill in at least the main symptom and duration.")

# Quick symptom checker
st.subheader("🚀 Quick Symptom Checker")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🤒 Cold/Flu Symptoms", key="cold_flu"):
        st.info("Rest, fluids, and monitor temperature. See a doctor if symptoms worsen or last >10 days.")

with col2:
    if st.button("🤕 Minor Injury", key="minor_injury"):
        st.info("Clean wound, apply bandage. For serious cuts or persistent pain, seek medical care.")

with col3:
    if st.button("😰 Stress/Anxiety", key="stress_anxiety"):
        st.info("Try deep breathing, exercise, or meditation. Consider professional help if persistent.")

# Common conditions and advice
st.subheader("📋 Common Health Conditions")

with st.expander("🤧 Common Cold"):
    st.write("**Symptoms:** Runny nose, sneezing, cough, sore throat")
    st.write("**Home care:** Rest, fluids, throat lozenges, humidifier")
    st.write("**See doctor if:** Symptoms last >10 days, high fever, severe headache")

with st.expander("🤒 Fever"):
    st.write("**Home care:** Rest, fluids, paracetamol/ibuprofen, cool compress")
    st.write("**See doctor if:** Fever >101.3°F (38.5°C), lasts >3 days, severe symptoms")

with st.expander("🤕 Headache"):
    st.write("**Home care:** Rest, hydration, dark room, cold/warm compress")
    st.write("**See doctor if:** Sudden severe headache, with fever, vision changes")

with st.expander("😷 Cough"):
    st.write("**Home care:** Honey, warm liquids, humidifier, avoid irritants")
    st.write("**See doctor if:** Blood in cough, persistent >3 weeks, with fever")

# Statistics in sidebar
if st.sidebar.button("📊 Usage Statistics", key="stats"):
    st.sidebar.write(f"Total consultations: {len(st.session_state.chat_history)}")
    if st.session_state.user_profile:
        st.sidebar.write(f"User location: {st.session_state.user_profile.get('location', 'Not specified')}")
        st.sidebar.write(f"User age: {st.session_state.user_profile.get('age', 'Not specified')}")

# Emergency contacts
st.subheader("🚨 Emergency Contacts")
st.write("🇮🇳 India: 102 (Medical Emergency)")
st.write("🇺🇸 USA: 911")
st.write("🇬🇧 UK: 999")
st.write("🌍 International: Check your local emergency number")

# Footer
st.markdown("---")
st.write("🌍 Supporting SDG Goal 3: Good Health and Well-being")
st.write("Available in multiple languages • Accessible in low-bandwidth areas • Free for all")
st.write("For emergency situations, always call your local emergency number")

# Feedback section
st.subheader("📝 Feedback")
feedback = st.text_area("How was your experience? Any suggestions?", key="feedback")
if st.button("Submit Feedback", key="submit_feedback"):
    if feedback:
        st.success("Thank you for your feedback!")
    else:
        st.error("Please enter your feedback before submitting.")