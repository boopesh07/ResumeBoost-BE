import streamlit as st
import requests

st.title("Resume Tailoring Tool")

# Add custom CSS to center the buttons
st.markdown(
    """
    <style>
    .centered-buttons {
        display: flex;
        justify-content: center;
        gap: 20px;
    }
    .stButton>button {
        width: 200px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Input sections for resume and job description
resume_text = st.text_area("Paste your resume here:")
job_description = st.text_area("Paste the job description here:")

# Create a container for the buttons and center them
st.markdown('<div class="centered-buttons">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Generate Tailored Resume"):
        response = requests.post("http://127.0.0.1:5000/generate_resume", json={
            "resume_text": resume_text,
            "job_description": job_description
        })
        if response.status_code == 200:
            result = response.json()
            # Display Tailored Resume
            tailored_resume = result.get('tailored_resume')
            st.text_area("Tailored Resume:", value=tailored_resume, height=300)

            # Display the keywords inserted
            keywords_inserted = result.get('keywords_inserted')
            st.text_area("Keywords Inserted:", value=keywords_inserted, height=300)

            # Display Score improvement
            score_improvement = result.get('score_improvement')
            st.text_area("Score Improvement:", value=score_improvement, height=100)

            # Display the project suggestions
            project_suggestions = result.get('project_suggestions')
            st.text_area("Project Suggestions:", value=project_suggestions, height=200)
        else:
            st.error("Error generating tailored resume")

with col2:
    if st.button("Generate Cover Letter"):
        response = requests.post("http://127.0.0.1:5000/generate_cover_letter", json={
            "resume_text": resume_text,
            "job_description": job_description
        })
        if response.status_code == 200:
            cover_letter = response.json().get('cover_letter')
            st.text_area("Cover Letter:", value=cover_letter, height=300)
        else:
            st.error("Error generating cover letter")
st.markdown('</div>', unsafe_allow_html=True)
