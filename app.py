import streamlit as st
from pdfminer.high_level import extract_text
import re

# Simple Skill Matching Logic (No SpaCy needed!)
SKILLS_DB = [
    "Java", "Python", "SQL", "React", "Spring Boot", "HTML", "CSS", 
    "JavaScript", "C++", "C", "Data Structures", "Arduino", "IoT",
    "Canva", "Machine Learning", "Git", "GitHub", "Node.js"
]

def extract_skills_simple(text):
    # Text ni mukkalu ga chesi (split), skills tho match cheyali
    # Case sensitive kakunda check chesthunnam
    found_skills = []
    # Removing special characters for clean matching
    clean_text = re.sub(r'[^\w\s]', ' ', text) 
    words = clean_text.split()
    
    for skill in SKILLS_DB:
        if skill.lower() in [w.lower() for w in words]:
            found_skills.append(skill)
    return list(set(found_skills))

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🚀")

st.title("AI Resume Analyzer 🚀")
st.markdown("---")

uploaded_file = st.file_uploader("Upload Your Resume (PDF format)", type=["pdf"])

if uploaded_file is not None:
    with st.spinner('Reading your resume...'):
        # 1. Extract Text
        text = extract_text(uploaded_file)
        
        # 2. Basic Info Extraction (Regex)
        email_match = re.search(r'\S+@\S+', text)
        phone_match = re.search(r'\b\d{10}\b', text)
        
        email = email_match.group() if email_match else "Not Found"
        phone = phone_match.group() if phone_match else "Not Found"
        
        # 3. Skill Extraction
        skills = extract_skills_simple(text)
        
        # --- UI DISPLAY ---
        st.success("Analysis Complete!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📌 Contact Info")
            st.write(f"**Email:** {email}")
            st.write(f"**Phone:** {phone}")
            
        with col2:
            st.subheader("💡 Identified Skills")
            if skills:
                for s in skills:
                    st.markdown(f"- {s}")
            else:
                st.warning("No matching skills found from our DB.")

        # Progress Bar Logic
        st.markdown("---")
        score = min(len(skills) * 15, 100)
        st.subheader(f"Resume Strength Score: {score}%")
        st.progress(score / 100)
        
        if score < 50:
            st.error("Tip: Add more technical keywords like 'Spring Boot' or 'Data Structures'.")
        else:
            st.balloons()
            st.success("Great! Your resume has a strong technical foundation.")