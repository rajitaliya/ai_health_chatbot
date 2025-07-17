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
        # Using microsoft/DialoGPT-small for better conversational responses
        ai_model = pipeline(
            "text-generation",
            model="microsoft/DialoGPT-small",
            max_length=200,
            do_sample=True,
            temperature=0.8,
            top_p=0.9,
            pad_token_id=50256
        )
        return ai_model
    except Exception as e:
        st.error(f"Error loading AI model: {e}")
        return None

# Load AI model
ai_model = load_health_ai()

# Medical knowledge base for specific conditions
MEDICAL_CONDITIONS = {
    'headache': {
        'causes': ['tension', 'dehydration', 'stress', 'lack of sleep', 'eye strain'],
        'treatments': ['rest in dark room', 'cold compress on forehead', 'gentle neck massage', 'stay hydrated'],
        'when_to_seek_help': 'sudden severe headache, headache with fever, vision changes'
    },
    'fever': {
        'causes': ['infection', 'inflammation', 'heat exhaustion', 'medication reaction'],
        'treatments': ['paracetamol/acetaminophen', 'cool compress', 'light clothing', 'plenty of fluids'],
        'when_to_seek_help': 'fever above 103°F (39.4°C), persistent fever over 3 days'
    },
    'cough': {
        'causes': ['cold', 'flu', 'allergies', 'throat irritation', 'acid reflux'],
        'treatments': ['honey (if over 1 year)', 'warm tea', 'steam inhalation', 'throat lozenges'],
        'when_to_seek_help': 'blood in cough, persistent cough over 3 weeks, difficulty breathing'
    },
    'nausea': {
        'causes': ['food poisoning', 'motion sickness', 'pregnancy', 'medication side effects'],
        'treatments': ['ginger tea', 'BRAT diet', 'small frequent meals', 'avoid strong odors'],
        'when_to_seek_help': 'severe dehydration, blood in vomit, persistent vomiting'
    },
    'stomach pain': {
        'causes': ['indigestion', 'gas', 'food poisoning', 'stress', 'menstrual cramps'],
        'treatments': ['heat pad', 'gentle movement', 'bland foods', 'avoid trigger foods'],
        'when_to_seek_help': 'severe abdominal pain, pain with fever, persistent pain'
    },
    'fatigue': {
        'causes': ['lack of sleep', 'stress', 'poor nutrition', 'dehydration', 'underlying conditions'],
        'treatments': ['adequate sleep 7-9 hours', 'balanced nutrition', 'regular exercise', 'stress management'],
        'when_to_seek_help': 'persistent fatigue despite rest, fatigue with other symptoms'
    },
    'sore throat': {
        'causes': ['viral infection', 'bacterial infection', 'allergies', 'dry air'],
        'treatments': ['warm salt water gargle', 'throat lozenges', 'honey', 'humidifier'],
        'when_to_seek_help': 'severe throat pain, difficulty swallowing, fever with sore throat'
    },
    'dizziness': {
        'causes': ['dehydration', 'low blood sugar', 'inner ear problems', 'medication effects'],
        'treatments': ['sit or lie down', 'stay hydrated', 'avoid sudden movements', 'adequate nutrition'],
        'when_to_seek_help': 'dizziness with chest pain, severe dizziness, dizziness with fainting'
    }
}

def identify_condition(symptoms_text):
    """Identify the most likely condition from symptoms"""
    symptoms_lower = symptoms_text.lower()
    
    # Check for specific conditions
    for condition, info in MEDICAL_CONDITIONS.items():
        if condition in symptoms_lower:
            return condition
    
    # Check for related terms
    if any(term in symptoms_lower for term in ['head', 'migraine']):
        return 'headache'
    elif any(term in symptoms_lower for term in ['temperature', 'hot', 'chills']):
        return 'fever'
    elif any(term in symptoms_lower for term in ['throat', 'swallow']):
        return 'sore throat'
    elif any(term in symptoms_lower for term in ['stomach', 'belly', 'abdominal']):
        return 'stomach pain'
    elif any(term in symptoms_lower for term in ['tired', 'exhausted', 'weak']):
        return 'fatigue'
    elif any(term in symptoms_lower for term in ['dizzy', 'lightheaded', 'vertigo']):
        return 'dizziness'
    elif any(term in symptoms_lower for term in ['vomit', 'sick', 'queasy']):
        return 'nausea'
    
    return None

def get_ai_health_advice(symptoms, severity, duration):
    """Generate AI health advice with condition-specific knowledge"""
    if ai_model is None:
        return "AI model not available. Please try again later."
    
    # Identify specific condition
    condition = identify_condition(symptoms)
    
    try:
        if condition and condition in MEDICAL_CONDITIONS:
            # Create condition-specific prompt
            condition_info = MEDICAL_CONDITIONS[condition]
            prompt = f"""Medical Case: Patient presents with {symptoms} (severity: {severity}/10, duration: {duration})
Condition Analysis: This appears to be {condition}
Common causes: {', '.join(condition_info['causes'])}
Recommended treatments: {', '.join(condition_info['treatments'])}

Professional medical advice:"""
            
        else:
            # General prompt for unknown conditions
            prompt = f"""Medical Case: Patient presents with {symptoms} (severity: {severity}/10, duration: {duration})
As a healthcare professional, I need to provide specific guidance for these symptoms.
Based on the symptom presentation and severity level, here is my clinical recommendation:"""
        
        # Generate AI response
        response = ai_model(
            prompt, 
            max_length=len(prompt.split()) + 70,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            top_p=0.8,
            repetition_penalty=1.3
        )
        
        # Extract generated text
        full_response = response[0]['generated_text']
        ai_advice = full_response.replace(prompt, "").strip()
        
        # If response is empty or too short, use condition-specific fallback
        if not ai_advice or len(ai_advice) < 15:
            if condition and condition in MEDICAL_CONDITIONS:
                condition_info = MEDICAL_CONDITIONS[condition]
                ai_advice = f"""For {condition} with severity {severity}/10:

**Likely causes:** {', '.join(condition_info['causes'])}

**Recommended treatments:**
• {condition_info['treatments'][0].title()}
• {condition_info['treatments'][1].title()}
• {condition_info['treatments'][2].title()}

**Seek immediate medical attention if:** {condition_info['when_to_seek_help']}"""
            else:
                ai_advice = f"""For {symptoms} with severity {severity}/10:
• Monitor symptoms closely and track any changes
• Apply appropriate supportive care measures
• Maintain hydration and adequate rest
• Consider over-the-counter relief if suitable"""
        
        # Add condition-specific warning if applicable
        if condition and condition in MEDICAL_CONDITIONS:
            ai_advice += f"\n\n⚠️ **Important:** Seek medical attention if you experience: {MEDICAL_CONDITIONS[condition]['when_to_seek_help']}"
        
        ai_advice += "\n\n🩺 **Disclaimer:** This is AI-generated guidance based on symptom analysis. Always consult a healthcare professional for proper diagnosis and treatment."
        
        return ai_advice
    
    except Exception as e:
        # Enhanced fallback with condition-specific advice
        if condition and condition in MEDICAL_CONDITIONS:
            condition_info = MEDICAL_CONDITIONS[condition]
            return f"""**{condition.title()} Management (Severity: {severity}/10):**

**Immediate care:**
• {condition_info['treatments'][0].title()}
• {condition_info['treatments'][1].title()}

**Additional measures:**
• {condition_info['treatments'][2].title()}
• Monitor for improvement over 24-48 hours

**Seek medical help if:** {condition_info['when_to_seek_help']}

🩺 **Note:** This is general guidance. Consult a healthcare professional for proper evaluation."""
        else:
            return f"""**Symptom Management for {symptoms}:**
• Apply appropriate supportive care
• Monitor symptom progression
• Maintain hydration and rest
• Seek professional medical advice if symptoms persist or worsen

🩺 **Important:** Always consult a healthcare professional for proper diagnosis and treatment."""

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
chat_input = st.text_input("Ask about your health concerns:", placeholder="e.g., I have a severe headache and feel nauseous")

if st.button("💭 Get AI Response") and chat_input:
    if ai_model is not None:
        with st.spinner("🤖 AI is analyzing your specific symptoms..."):
            # Identify condition for better response
            condition = identify_condition(chat_input)
            
            try:
                if condition and condition in MEDICAL_CONDITIONS:
                    condition_info = MEDICAL_CONDITIONS[condition]
                    chat_prompt = f"""Patient presents with: "{chat_input}"
Clinical assessment: This appears to be {condition}
Known causes: {', '.join(condition_info['causes'])}
Standard treatments: {', '.join(condition_info['treatments'])}

Professional medical guidance:"""
                else:
                    chat_prompt = f"""Patient concern: "{chat_input}"
As a medical professional, I need to provide specific guidance for this presentation.
Clinical assessment and recommendations:"""
                
                response = ai_model(
                    chat_prompt, 
                    max_length=len(chat_prompt.split()) + 60,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.8,
                    repetition_penalty=1.3
                )
                
                ai_response = response[0]['generated_text'].replace(chat_prompt, "").strip()
                
                # Enhanced fallback with condition-specific advice
                if not ai_response or len(ai_response) < 15:
                    if condition and condition in MEDICAL_CONDITIONS:
                        condition_info = MEDICAL_CONDITIONS[condition]
                        ai_response = f"""**{condition.title()} Assessment:**

**What you can do now:**
• {condition_info['treatments'][0].title()}
• {condition_info['treatments'][1].title()}
• {condition_info['treatments'][2].title()}

**When to seek immediate help:** {condition_info['when_to_seek_help']}"""
                    else:
                        ai_response = f"""**For your concern:** "{chat_input}"
• Apply appropriate supportive care measures
• Monitor your symptoms for any changes
• Consider basic comfort measures
• Seek professional evaluation if symptoms persist"""
                
                st.write("**🩺 AI Health Assistant:**")
                st.write(ai_response)
                
                # Add condition-specific warning
                if condition and condition in MEDICAL_CONDITIONS:
                    st.warning(f"⚠️ **Seek immediate medical attention if:** {MEDICAL_CONDITIONS[condition]['when_to_seek_help']}")
                
                st.info("🩺 **Medical Disclaimer:** This is AI-generated guidance based on symptom analysis. Always consult a healthcare professional for proper diagnosis and treatment.")
                
            except Exception as e:
                st.write("**🩺 AI Health Assistant:**")
                if condition and condition in MEDICAL_CONDITIONS:
                    condition_info = MEDICAL_CONDITIONS[condition]
                    st.write(f"""**{condition.title()} Management:**

**Immediate care:**
• {condition_info['treatments'][0].title()}
• {condition_info['treatments'][1].title()}

**Additional measures:**
• {condition_info['treatments'][2].title()}
• Monitor for improvement

**Seek help if:** {condition_info['when_to_seek_help']}""")
                else:
                    st.write(f"""**For your concern:** "{chat_input}"
• Apply appropriate supportive care
• Monitor symptom progression
• Maintain hydration and rest
• Seek professional medical advice if needed""")
                
                st.info("🩺 **Note:** This is general medical guidance. Consult a healthcare professional for proper evaluation.")
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