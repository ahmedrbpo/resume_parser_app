import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from parser import extract_text_from_file, extract_resume_data, match_keywords
from database import init_db, save_resume

# Init DB
init_db()

# Load auth config
with open('auth_config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'], config['cookie']['name'], config['cookie']['key'], config['cookie']['expiry_days']
)

name, auth_status, username = authenticator.login('Login', 'main')

if auth_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Logged in as: {username}")

    st.title("📄 Resume Parser + JD Matcher")

    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
    with col2:
        jd_input = st.text_area("Paste Job Description or Keywords")

    if st.button("Parse Resume"):
        if uploaded_file and jd_input:
            resume_text = extract_text_from_file(uploaded_file)
            resume_data = extract_resume_data(resume_text)
            keywords = [kw.strip() for kw in jd_input.split(',')]
            matched, unmatched = match_keywords(resume_text, keywords)
            resume_data['matched'] = matched
            resume_data['unmatched'] = unmatched

            st.subheader("📋 Extracted Resume Info")
            st.write(resume_data)

            st.subheader("✅ Matched Keywords")
            st.success(", ".join(matched) or "None")

            st.subheader("❌ Missing Keywords")
            st.error(", ".join(unmatched) or "None")

            save_resume(username, resume_data)
        else:
            st.warning("Please upload a resume and provide keywords.")
elif auth_status is False:
    st.error("Incorrect credentials")
elif auth_status is None:
    st.info("Please log in to continue.")
