import streamlit as st
from pdfminer.high_level import extract_text
import re
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

# 2. Live LLM Integration Function
def analyze_with_claude(resume_text, job_description, api_key):
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        system_instruction = (
            "You are an expert Technical Recruitment Specialist and AI Talent Agent. "
            "Analyze the provided resume text against the Job Description. Do not simply look for keyword matches; "
            "evaluate the underlying technical complexity, project scope, and engineering competencies."
        )
        
        user_prompt = f"""
        Please evaluate this profile:
        
        ### JOB DESCRIPTION REQUIREMENTS:
        {job_description}
        
        ### CANDIDATE RESUME TEXT:
        {resume_text}
        
        Provide your response in clean markdown with semantic matching, critical gaps, and optimizations.
        """
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0,
            system=system_instruction,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

# 3. Streamlit Page Configuration
st.set_page_config(page_title="Agentic AI Resume Analyzer", page_icon="🚀", layout="wide")

st.title("Agentic AI Resume Analyzer & Matcher 🚀")
st.markdown("Automated semantic profile evaluation powered by Claude AI.")
st.markdown("---")

# Sidebar settings with the Free Demo Mode switch
st.sidebar.header("⚙️ Configuration")
demo_mode = st.sidebar.checkbox("Enable Demo Mode (No Key Needed)", value=False)

if not demo_mode:
    api_key_input = st.sidebar.text_input("Enter Anthropic API Key", type="password")
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

# Processing and Execution Lifecycle
if uploaded_file is not None and target_jd:
    if st.button("Run Deep AI Screening Analysis", type="primary"):
        if not demo_mode and not api_key_input:
            st.warning("Please provide an Anthropic API Key or enable Demo Mode in the sidebar.")
        else:
            with st.spinner('Parsing document and orchestrating Engine...'):
                # Document Extraction Layer
                text = extract_text(uploaded_file)
                
                # Regex Extraction Layer
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
                
                st.markdown("### 🧠 Claude AI Deep Semantic Analysis")
                
                # Render logic branching based on sidebar state
                if demo_mode:
                    st.markdown("""
                    🎯 **Semantic Match Assessment** The candidate profile exhibits strong core capabilities in backend architectures and automated data processing pipelines. Project implementations match 85% of structural expectations.
                    
                    ⚠️ **Critical Tech Stack Gaps** * Lack of explicit production monitoring configurations.
                    * Abstract definitions in data orchestration layers.
                    
                    💡 **Actionable Optimization Steps** 1. **Quantify Metrics:** Convert project statements into numeric successes (e.g., 'Optimized text processing latency by 30%').
                    2. **Highlight API Design:** Explicitly call out security architectures used during microservice connections.
                    3. **Refine Context Windows:** Frame parsing library use cases around computational footprint control.
                    
                    📈 **AI Alignment Score** **88% Alignment** — Profile structurally matches target criteria with minor optimizations required in architectural descriptions.
                    """)
                    st.balloons()
                else:
                    ai_analysis_result = analyze_with_claude(text, target_jd, api_key_input)
                    st.markdown(ai_analysis_result)
                    st.balloons()
else:
    st.info("Please paste a target Job Description and upload a resume PDF to trigger the intelligent recruitment analysis.")