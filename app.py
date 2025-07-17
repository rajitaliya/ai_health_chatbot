import streamlit as st
import time
from transformers import pipeline
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="AI Health Assistant", 
    layout="centered"
)

# Cache the model loading
@st.cache_resource
def load_health_ai():
    """Load a lightweight AI model for health guidance"""
    try:
        # Using a small, free model for text generation
        ai_model = pipeline(
            "text-generation",
            model="distilgpt2",
            max_length=150,
            do_sample=True,
            temperature=0.7,
            pad_token_id=50256
        )
        return ai_model
    except Exception as e:
        st.error(f"Error loading AI model: {e}")
        return None

# Load AI model
ai_model = load_health_ai()

def get_ai_health_advice(symptoms, severity, duration):
    """Generate AI health advice"""
    if ai_model is None:
        return "AI model not available. Please try again later."
    
    try:
        # Create health-focused prompt
        prompt = f"""
        
        Please provide general health advice, potential home remedies, and when to seek medical attention.
        Health advice for {symptoms} (severity: {severity}/10, duration: {duration}): 
        
        """
        
        # Generate AI response
        response = ai_model(prompt, max_length=100, num_return_sequences=1)
        ai_advice = response[0]['generated_text'].replace(prompt, "").strip()
        
        # Add safety disclaimer
        ai_advice += "\n\n⚠️ This is AI-generated guidance. Always consult a healthcare professional."
        
        return ai_advice
    except:
        return "Unable to generate AI response. Please consult a healthcare professional."

st.title("🩺 AI Health Assistant")
st.write("Free, accessible health guidance powered by AI")

# Show AI model status
if ai_model is not None:
    st.success("✅ AI Model Ready")
else:
    st.error("❌ AI Model Not Available")

# Disclaimer
st.warning("⚠️ Important: This tool provides preliminary health guidance only. Always consult with a qualified healthcare provider for serious symptoms.")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

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
    
    if int(severity) >= 8:
        return True
    
    return False

# Generate basic health advice
def generate_health_advice(main_symptom, other_symptoms, duration, severity, medical_history, medications, current_condition):
    # Emergency check
    if check_emergency_symptoms(main_symptom, other_symptoms, severity, current_condition):
        return {
            'type': 'emergency',
            'advice': "⚠️ SEEK IMMEDIATE MEDICAL ATTENTION! Visit the nearest emergency room or call emergency services."
        }
    
    # Get AI advice
    ai_advice = get_ai_health_advice(main_symptom, severity, duration)
    
    # Basic advice based on common symptoms
    advice = []
    main_symptom_lower = main_symptom.lower()
    
    if 'fever' in main_symptom_lower:
        advice.append("🌡️ For fever: Rest, stay hydrated, take paracetamol as directed")
    
    if 'headache' in main_symptom_lower:
        advice.append("🧠 For headache: Rest in dark room, apply cold compress, stay hydrated")
    
    if 'cough' in main_symptom_lower:
        advice.append("🤧 For cough: Stay hydrated, use honey, avoid irritants")
    
    if 'nausea' in main_symptom_lower:
        advice.append("🤢 For nausea: Try ginger tea, eat bland foods, avoid strong odors")
    
    # Add general advice
    advice.extend([
        "💧 Stay well hydrated",
        "🛌 Get adequate rest",
        "🍲 Eat nutritious foods"
    ])
    
    return {
        'type': 'general',
        'ai_advice': ai_advice,
        'basic_advice': advice
    }

# User profile section
st.subheader("👤 User Profile (Optional)")
col1, col2 = st.columns(2)

with col1:
    user_age = st.selectbox("Age Group", ["Select", "0-12", "13-17", "18-30", "31-50", "51-65", "65+"])
    user_gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])

with col2:
    user_location = st.selectbox("Location", ["Select", "Urban", "Rural", "Semi-urban"])
    user_language = st.selectbox("Language", ["English", "Hindi", "Spanish", "French"])

# Quick symptom checker
st.subheader("🚀 Quick Symptom Checker")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🤒 Cold/Flu"):
        st.info("**Home Care:** Rest, fluids, monitor temperature. See doctor if symptoms worsen.")

with col2:
    if st.button("🤕 Minor Injury"):
        st.info("**Home Care:** Clean wound, apply bandage. Seek medical care if serious.")

with col3:
    if st.button("😰 Stress/Anxiety"):
        st.info("**Home Care:** Deep breathing, exercise, meditation. Get help if persistent.")

# AI Chat Interface
st.subheader("💬 Chat with AI Health Assistant")
chat_input = st.text_input("Ask about your health concerns:", placeholder="e.g., I have a headache and feel tired")

if st.button("💭 Get AI Response") and chat_input:
    if ai_model is not None:
        with st.spinner("🤖 AI is thinking..."):
            ai_response = get_ai_health_advice(chat_input, "5", "recent")
            st.write("**AI Health Assistant:**")
            st.write(ai_response)
    else:
        st.error("AI model not available.")

# Detailed health assessment
st.subheader("🔍 Detailed Health Assessment")

with st.form("health_assessment_form"):
    # Main symptom
    main_symptom = st.text_input("Main symptom or concern:", placeholder="e.g., headache, fever, cough")
    
    # Duration
    duration = st.selectbox("Duration:", 
                           ["Select", "Less than 1 day", "1-3 days", "4-7 days", "1-2 weeks", "More than 2 weeks"])
    
    # Severity
    severity = st.slider("Severity (1-10):", 1, 10, 5)
    
    # Other symptoms
    other_symptoms = st.multiselect("Other symptoms:", 
                                  ["Fever", "Headache", "Nausea", "Fatigue", "Cough", "Chest pain"])
    
    # Medical history
    medical_history = st.text_input("Medical history:", placeholder="e.g., diabetes, hypertension")
    
    # Current medications
    medications = st.text_input("Current medications:", placeholder="e.g., aspirin, insulin")
    
    # Current condition
    current_condition = st.text_input("Current condition:", placeholder="Describe how you're feeling")
    
    # Submit button
    submitted = st.form_submit_button("Get Health Guidance")
    
    if submitted:
        if main_symptom and duration != "Select":
            with st.spinner("🤖 Analyzing symptoms..."):
                advice_result = generate_health_advice(
                    main_symptom, other_symptoms, duration, severity, 
                    medical_history, medications, current_condition
                )
                
                if advice_result['type'] == 'emergency':
                    st.error(advice_result['advice'])
                else:
                    st.success("🤖 AI Health Guidance:")
                    st.write(advice_result['ai_advice'])
                    
                    st.info("📋 Basic Recommendations:")
                    for advice_item in advice_result['basic_advice']:
                        st.write(f"• {advice_item}")
                    
                    st.info("📞 When to seek help:")
                    st.write("• If symptoms worsen or persist")
                    st.write("• If you develop new symptoms")
                    st.write("• If you're unsure about your condition")
                
                # Track usage
                st.session_state.chat_history.append({
                    'timestamp': time.time(),
                    'symptoms': main_symptom,
                    'advice_type': advice_result['type']
                })
        else:
            st.error("Please fill in main symptom and duration.")

# Common conditions
st.subheader("📋 Common Health Conditions")

with st.expander("🤧 Common Cold"):
    st.write("**Symptoms:** Runny nose, sneezing, cough, sore throat")
    st.write("**Home care:** Rest, fluids, throat lozenges")
    st.write("**See doctor if:** Symptoms last >10 days, high fever")

with st.expander("🤒 Fever"):
    st.write("**Home care:** Rest, fluids, paracetamol, cool compress")
    st.write("**See doctor if:** Fever >101.3°F, lasts >3 days")

with st.expander("🤕 Headache"):
    st.write("**Home care:** Rest, hydration, dark room, compress")
    st.write("**See doctor if:** Sudden severe headache, with fever")

# Emergency contacts
st.subheader("🚨 Emergency Contacts")
st.write("🇮🇳 India: 102")
st.write("🇺🇸 USA: 911")
st.write("🇬🇧 UK: 999")

# Statistics
st.subheader("📊 Usage Statistics")
if st.button("View Statistics"):
    st.write(f"Total consultations: {len(st.session_state.chat_history)}")

# Footer
st.markdown("---")
st.write("🤖 Powered by AI • 🌍 Supporting Good Health and Well-being")
st.write("Free for all • For emergencies, call your local emergency number")

# Feedback
st.subheader("📝 Feedback")
with st.form("feedback_form"):
    feedback_text = st.text_input("Your feedback:")
    feedback_submitted = st.form_submit_button("Submit")
    
    if feedback_submitted and feedback_text:
        st.success("Thank you for your feedback!")