import streamlit as st
from pdfminer.high_level import extract_text
import re
import anthropic  # New: The official Claude AI library

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

# New: LLM Logic to call Claude
def analyze_with_claude(resume_text, job_description, api_key):
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        system_instruction = (
            "You are an expert Technical Recruitment Specialist and AI Talent Agent. "
            "Analyze the provided resume text against the Job Description. Do not simply look for keyword matches; "
            "evaluate the underlying technical complexity, project scope, and engineering competencies. "
            "Be critical, precise, and highly constructive."
        )
        
        user_prompt = f"""
        Please evaluate this profile:
        
        ### JOB DESCRIPTION REQUIREMENTS:
        {job_description}
        
        ### CANDIDATE RESUME TEXT:
        {resume_text}
        
        Provide your response in clean markdown with the following specific sections:
        1. 🎯 **Semantic Match Assessment** (How well do their projects and skills conceptually align?)
        2. ⚠️ **Critical Tech Stack Gaps** (What mandatory frameworks or tools are completely missing?)
        3. 💡 **Actionable Optimization Steps** (Provide 3 specific bullet points to improve this resume for this exact role.)
        4. 📈 **AI Alignment Score** (Provide a concise structural justification and a final percentage fit from 0% to 100%.)
        """
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0,
            system=system_instruction,
            messages=[{"role": "user", "content": user_prompt}]
        )
        # Extract the text content from the response object
        return message.content[0].text
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

# Streamlit Page Setup
st.set_page_config(page_title="Agentic AI Resume Analyzer", page_icon="🚀", layout="wide")

st.title("Agentic AI Resume Analyzer & Matcher 🚀")
st.markdown("Automated semantic profile evaluation powered by Claude AI.")
st.markdown("---")

# Sidebar for secure API configuration
st.sidebar.header("⚙️ Configuration")
api_key_input = st.sidebar.text_input("Enter Anthropic API Key", type="password", help="Your key is processed locally and never stored.")

# Main Application Form UI Split
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📋 Step 1: Target Job Description")
    target_jd = st.text_area("Paste the job requirements/description here...", height=200)

with col_right:
    st.subheader("📄 Step 2: Candidate Profile")
    uploaded_file = st.file_uploader("Upload Resume (PDF format)", type=["pdf"])

st.markdown("---")

# Processing Flow
if uploaded_file is not None and target_jd:
    if st.button("Run Deep AI Screening Analysis", type="primary"):
        if not api_key_input:
            st.warning("Please provide an Anthropic API Key in the sidebar to run the LLM analysis.")
        else:
            with st.spinner('Parsing document and orchestrating Claude Engine...'):
                # 1. Parsing Layer
                text = extract_text(uploaded_file)
                
                # 2. Local Regular Expression Extractions
                email_match = re.search(r'\S+@\S+', text)
                phone_match = re.search(r'\b\d{10}\b', text)
                email = email_match.group() if email_match else "Not Found"
                phone = phone_match.group() if phone_match else "Not Found"
                local_skills = extract_skills_simple(text)
                
                # Display structural information extracted locally
                st.success("Document Parsing Complete!")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.info(f"**Metadata Found**\n* Email: {email}\n* Phone: {phone}")
                with c2:
                    st.info(f"**Core DB Skills Found:** {', '.join(local_skills) if local_skills else 'None'}")
                
                st.markdown("### 🧠 Claude AI Deep Semantic Analysis")
                # 3. LLM Orchestration Layer
                ai_analysis_result = analyze_with_claude(text, target_jd, api_key_input)
                
                # Render the markdown report beautifully directly on screen
                st.markdown(ai_analysis_result)
                st.balloons()
else:
    st.info("Please paste a target Job Description and upload a resume PDF to trigger the intelligent recruitment analysis.")
