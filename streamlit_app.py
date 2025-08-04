import streamlit as st
import docx2txt
from pdfminer.high_level import extract_text
import re
from collections import Counter
import sqlite3
from datetime import datetime

# ---------- DATABASE SETUP ----------
DB_FILE = 'resumes.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            skills TEXT,
            roles TEXT,
            score TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO resumes (name, email, phone, skills, roles, score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['name'], data['email'], data['phone'],
        ', '.join(data['skills']), data['roles'], data['score']
    ))
    conn.commit()
    conn.close()

# ---------- TEXT EXTRACTION ----------
def extract_text_from_file(file):
    if file.name.endswith('.pdf'):
        return extract_text(file)
    elif file.name.endswith('.docx'):
        return docx2txt.process(file)
    elif file.name.endswith('.txt'):
        return file.read().decode('utf-8')
    return ""

def clean_text(text):
    return re.sub(r'[^a-z\s]', '', text.lower())

def extract_keywords(text):
    words = clean_text(text).split()
    return Counter(words)

def match_score(resume_words, jd_words):
    matched = sum((resume_words & jd_words).values())
    total = sum(jd_words.values())
    return int((matched / total) * 100) if total > 0 else 0

def highlight_keywords(resume_words, jd_words):
    matched = list((resume_words & jd_words).elements())
    matched_set = set(matched)
    jd_set = set(jd_words.elements())
    return sorted(matched_set), sorted(jd_set - matched_set)

def extract_resume_info(text):
    info = {}

    email = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    info['email'] = email[0] if email else None

    phone = re.findall(r'\+?\d[\d\s\-()]{7,}\d', text)
    info['phone'] = phone[0] if phone else None

    lines = text.strip().split('\n')
    for line in lines:
        clean = line.strip()
        if 2 <= len(clean.split()) <= 4 and not any(c.isdigit() for c in clean):
            info['name'] = clean
            break

    skill_keywords = ['python', 'java', 'c++', 'sql', 'flask', 'django', 'aws',
                      'javascript', 'excel', 'pandas', 'react', 'machine learning']
    found_skills = {word for word in skill_keywords if re.search(r'\b' + re.escape(word) + r'\b', text.lower())}
    info['skills'] = list(found_skills)

    rr = re.findall(r'(responsibilities|experience|work experience|roles).*?:?\n([\s\S]{0,1000})', text, re.IGNORECASE)
    info['roles'] = max(rr, key=lambda x: len(x[1]))[1].strip() if rr else None

    return info

# ---------- STREAMLIT UI ----------
init_db()
st.set_page_config(page_title="Resume Parser", layout="centered")
st.title("📄 Resume Parser & JD Keyword Matcher")

st.markdown("Upload a **Resume**, and enter **keywords or a Job Description** to validate.")

resume_file = st.file_uploader("Upload Resume (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])
jd_input = st.text_area("Paste Job Description or Keywords (comma or space separated)", height=150)

if resume_file and jd_input.strip():
    resume_text = extract_text_from_file(resume_file)
    resume_words = extract_keywords(resume_text)
    jd_clean = clean_text(jd_input)
    jd_words = Counter(jd_clean.split())

    score = match_score(resume_words, jd_words)
    match = f"{score}% match"
    matched_keywords, unmatched_keywords = highlight_keywords(resume_words, jd_words)

    resume_info = extract_resume_info(resume_text)
    resume_info['score'] = match

    st.success(f"✅ Resume Match Score: {match}")
    with st.expander("📌 Matched Keywords"):
        st.write(", ".join(matched_keywords))
    with st.expander("⚠️ Missing Keywords"):
        st.write(", ".join(unmatched_keywords))
    with st.expander("📄 Extracted Resume Info"):
        st.write(f"**Name:** {resume_info.get('name')}")
        st.write(f"**Email:** {resume_info.get('email')}")
        st.write(f"**Phone:** {resume_info.get('phone')}")
        st.write(f"**Skills:** {', '.join(resume_info.get('skills'))}")
        st.text_area("Roles & Responsibilities:", resume_info.get('roles'), height=200)

    if st.button("💾 Save to Database"):
        save_to_db(resume_info)
        st.success("✅ Resume data saved!")

if st.checkbox("📊 View Saved Submissions"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name, email, phone, skills, score, created_at FROM resumes ORDER BY created_at DESC")
    for row in c.fetchall():
        st.markdown(f"""
        **👤 Name**: {row[0]}  
        **📧 Email**: {row[1]}  
        **📱 Phone**: {row[2]}  
        **🛠️ Skills**: {row[3]}  
        **✅ Score**: {row[4]}  
        **🕒 Timestamp**: {row[5]}  
        ---
        """)
    conn.close()
