import streamlit as st
import requests
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="SDR Prep Gem ✨",
    page_icon="✨",
    layout="wide"
)

# --- GEMINI API INTEGRATION ---
def call_gemini(form_data):
    """
    Calls the Gemini API to get AI-generated insights for the SDR briefing.
    Uses Streamlit Secrets for the API key.
    """
    try:
        # Access the API key from Streamlit's secrets management
        api_key = st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.error("GEMINI_API_KEY not found in Streamlit Secrets. Please add it to your secrets.toml file or in the Streamlit Community Cloud settings.")
        st.stop()
        
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    prompt = f"""
        You are an expert sales strategist and coach at Snowflake, specializing in the MEDDPICC methodology. 
        Your task is to generate a complete pre-call briefing package for a Sales Development Representative based on the following information.

        **Prospect Information:**
        - Name: {form_data['personaName']}
        - Title: {form_data['title']}
        - Account: {form_data['accountName']}
        - Status: {form_data['status']}
        - LinkedIn Info: {form_data['linkedinInfo']}
        - Other Info: {form_data['supportingInfo']}

        Generate a JSON object with the following structure. Do not include any other text or markdown formatting.
    """

    # This is the JSON schema the AI will follow for its response
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "justification": {"type": "STRING"},
                    "useCase": {"type": "STRING"},
                    "discoveryQuestions": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "openingStatements": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "type": {"type": "STRING"},
                                "statement": {"type": "STRING"}
                            },
                            "required": ["type", "statement"]
                        }
                    }
                },
                "required": ["justification", "useCase", "discoveryQuestions", "openingStatements"]
            }
        }
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        result = response.json()

        if 'candidates' in result and result['candidates']:
            raw_json = result['candidates'][0]['content']['parts'][0]['text']
            return json.loads(raw_json)
        else:
            st.error("Error: Invalid response structure from Gemini API.")
            st.json(result) # Display the invalid response for debugging
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Error: API call failed: {e}")
        return None
    except json.JSONDecodeError:
        st.error("Error: Failed to decode JSON from API response.")
        return None


# --- HELPER FUNCTIONS ---
def get_customer_reference(use_case):
    """
    Returns a relevant customer reference based on the use case.
    """
    lower_case = use_case.lower()
    if 'application' in lower_case:
        return "Instacart built their data-intensive applications on Snowflake, allowing them to scale to millions of users while reducing their infrastructure costs by 30%."
    if 'ai' in lower_case or 'ml' in lower_case:
        return "Western Union leveraged Snowflake to reduce the development time for their fraud detection models by 75% and can now deploy new AI models in days instead of months."
    if 'finance' in lower_case:
        return "BlackRock runs its Aladdin platform on Snowflake, processing trillions of dollars in financial transactions and providing clients with near real-time investment insights."
    return "Capital One modernized their data stack with Snowflake to enable better customer experiences and faster innovation, all within a secure and governed environment."

# --- STREAMLIT UI ---
st.title("Snowflake SDR Prep Gem ✨")
st.markdown("Fill out the details below to generate a comprehensive, AI-powered pre-call briefing.")

# Use a form to gather all inputs and submit with a single button
with st.form(key='sdr_form'):
    st.subheader("1. Enter Prospect Details")
    col1, col2 = st.columns(2)
    with col1:
        persona_name = st.text_input("Persona Name", "Jane Doe")
        account_name = st.text_input("Account Name", "InnovateFin")
    with col2:
        title = st.text_input("Title", "VP of Engineering")
        status = st.radio("Status", ('Prospect', 'Customer'), horizontal=True)

    linkedin_info = st.text_area("Optional LinkedIn Info", "Recently promoted. Background in scaling distributed systems and cloud infrastructure. Posted an article last month about the challenges of managing multi-cloud data pipelines.", height=100)
    supporting_info = st.text_area("Other Supporting Info (Triggers, news, etc.)", "InnovateFin just announced a new AI-powered risk assessment product. They are hiring aggressively for data scientists and ML engineers.", height=100)
    
    submit_button = st.form_submit_button(label='✨ Generate AI Briefing')

# --- Main Logic ---
if submit_button:
    # Package form data
    form_data = {
        'personaName': persona_name,
        'title': title,
        'accountName': account_name,
        'status': status,
        'linkedinInfo': linkedin_info,
        'supportingInfo': supporting_info
    }

    with st.spinner("✨ The Gem is consulting the AI... please wait."):
        ai_data = call_gemini(form_data)

    if ai_data:
        st.balloons()
        st.header(f"Pre-Call Briefing: {form_data['personaName']} at {form_data['accountName']}")
        
        # Display At-a-Glance Intel
        st.subheader("1. At-a-Glance Intel")
        st.markdown(f"""
        - **Persona:** {form_data['personaName']}, {form_data['title']}
        - **Account:** {form_data['accountName']} ({form_data['status']})
        - **LinkedIn Intel:** {form_data['linkedinInfo'] or 'Not provided.'}
        - **Key Trigger Intel:** {form_data['supportingInfo'] or 'Not provided.'}
        """)
        st.divider()

        # Display "Why You, Why Now"
        st.subheader("2. The 'Why You, Why Now'")
        st.markdown(f"**✨ Justification:** *{ai_data['justification']}*")
        st.markdown(f"**✨ Recommended Use Case:** {ai_data['useCase']}")
        st.markdown(f"**- Relevant Customer Reference:** {get_customer_reference(ai_data['useCase'])}")
        st.divider()
        
        # Display Conversation Toolkit
        st.subheader("3. Conversation Toolkit")
        
        st.markdown("##### ✨ Powerful Opening Statements")
        openers_text = ""
        for opener in ai_data['openingStatements']:
            statement = opener['statement'].replace('[Persona Name]', form_data['personaName']).replace('[SDR Name]', '[Your Name]')
            openers_text += f"- **{opener['type']}:** \"{statement}\"\n"
        st.markdown(openers_text)

        st.markdown("##### ✨ MEDDPICC Discovery Questions")
        questions_text = ""
        for question in ai_data['discoveryQuestions']:
            questions_text += f"- {question}\n"
        st.markdown(questions_text)