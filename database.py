import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('resumes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        name TEXT,
        email TEXT,
        phone TEXT,
        skills TEXT,
        matched_keywords TEXT,
        unmatched_keywords TEXT,
        created_at TEXT
    )''')
    conn.commit()
    conn.close()

def save_resume(username, data):
    conn = sqlite3.connect('resumes.db')
    c = conn.cursor()
    c.execute('''INSERT INTO resumes 
        (username, name, email, phone, skills, matched_keywords, unmatched_keywords, created_at) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            username,
            data['name'], data['email'], data['phone'], data['skills'],
            ", ".join(data['matched']),
            ", ".join(data['unmatched']),
            datetime.now().isoformat()
        )
    )
    conn.commit()
    conn.close()
