import streamlit as st
from pdfminer.high_level import extract_text
import re
import google.generativeai as genai
import anthropic

# 1. Local Database Setup for Quick Matching
SKILLS_DB = [
    "Java", "Python", "SQL", "React", "Spring Boot", "HTML", "CSS", 
    "JavaScript", "C++", "C", "Data Structures", "Arduino", "IoT",
    "Canva", "Machine Learning", "Git", "GitHub", "Node.js"
]

def extract_skills_simple(text):
    found_skills = []
    clean_text = re.sub(r'[^\w\s]', ' ', text) 
    words = clean_text.split()
    for skill in SKILLS_DB:
        if skill.lower() in [w.lower() for w in words]:
            found_skills.append(skill)
    return list(set(found_skills))

# ==========================================
# LLM ENGINE LAYER
# ==========================================

# Engine A: Google Gemini (Free Tier)
def analyze_with_gemini(resume_text, job_description, api_key):
    try:
        genai.configure(api_key=api_key)
        system_instruction = (
            "You are an expert Technical Recruitment Specialist and AI Talent Agent. "
            "Analyze the provided resume text against the Job Description. Do not simply look for keyword matches; "
            "evaluate the underlying technical complexity, project scope, and engineering competencies."
        )
        user_prompt = f"### JOB DESCRIPTION:\n{job_description}\n\n### RESUME:\n{resume_text}"
        
        model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=system_instruction)
        response = model.generate_content(user_prompt, generation_config={"temperature": 0})
        return response.text
    except Exception as e:
        return f"⚠️ Gemini API Error: {str(e)}"

# Engine B: Anthropic Claude (For Your Recruiters)
def analyze_with_claude(resume_text, job_description, api_key):
    try:
        client = anthropic.Anthropic(api_key=api_key)
        system_instruction = (
            "You are an expert Technical Recruitment Specialist and AI Talent Agent. "
            "Analyze the provided resume text against the Job Description. Do not simply look for keyword matches; "
            "evaluate the underlying technical complexity, project scope, and engineering competencies."
        )
        user_prompt = f"### JOB DESCRIPTION:\n{job_description}\n\n### RESUME:\n{resume_text}"
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0,
            system=system_instruction,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"⚠️ Claude API Error: {str(e)}"

# ==========================================
# STREAMLIT UI LAYER
# ==========================================
st.set_page_config(page_title="Agentic AI Resume Analyzer", page_icon="🚀", layout="wide")

st.title("Multi-Engine AI Resume Analyzer & Matcher 🚀")
st.markdown("Automated semantic profile evaluation powered by Claude & Gemini AI.")
st.markdown("---")

# Sidebar settings
st.sidebar.header("⚙️ Configuration")

# Dropdown to choose the model provider
model_provider = st.sidebar.selectbox("Select AI Engine", ["Google Gemini (Free Tier)", "Anthropic Claude"])
demo_mode = st.sidebar.checkbox("Enable Demo Mode (No Key Needed)", value=False)

if not demo_mode:
    api_key_input = st.sidebar.text_input(f"Enter {model_provider} API Key", type="password")
else:
    api_key_input = "demo-active"

# Layout split for input variables
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📋 Step 1: Target Job Description")
    target_jd = st.text_area("Paste the job requirements/description here...", height=200)

with col_right:
    st.subheader("📄 Step 2: Candidate Profile")
    uploaded_file = st.file_uploader("Upload Resume (PDF format)", type=["pdf"])

st.markdown("---")

# Execution Lifecycle
if uploaded_file is not None and target_jd:
    if st.button("Run Deep AI Screening Analysis", type="primary"):
        if not demo_mode and not api_key_input:
            st.warning(f"Please provide a valid key for {model_provider} or enable Demo Mode.")
        else:
            with st.spinner('Parsing document and orchestrating Engine...'):
                text = extract_text(uploaded_file)
                
                email_match = re.search(r'\S+@\S+', text)
                phone_match = re.search(r'\b\d{10}\b', text)
                email = email_match.group() if email_match else "Not Found"
                phone = phone_match.group() if phone_match else "Not Found"
                local_skills = extract_skills_simple(text)
                
                st.success("Document Parsing Complete!")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.info(f"**Metadata Found**\n* Email: {email}\n* Phone: {phone}")
                with c2:
                    st.info(f"**Core DB Skills Found:** {', '.join(local_skills) if local_skills else 'None'}")
                
                st.markdown(f"### 🧠 {model_provider} Deep Semantic Analysis")
                
                if demo_mode:
                    st.markdown("""
                    🎯 **Semantic Match Assessment** The candidate profile exhibits strong core capabilities.
                    ⚠️ **Critical Tech Stack Gaps** * Lack of explicit production monitoring configurations.
                    💡 **Actionable Optimization Steps** 1. Quantify Metrics.
                    📈 **AI Alignment Score** **88% Alignment**
                    """)
                    st.balloons()
                else:
                    # Route execution based on dropdown selection
                    if model_provider == "Google Gemini (Free Tier)":
                        ai_analysis_result = analyze_with_gemini(text, target_jd, api_key_input)
                    else:
                        ai_analysis_result = analyze_with_claude(text, target_jd, api_key_input)
                        
                    st.markdown(ai_analysis_result)
                    st.balloons()
else:
    st.info("Please paste a target Job Description and upload a resume PDF to trigger the intelligent recruitment analysis.")
