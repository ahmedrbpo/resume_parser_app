import re
import docx2txt
import pdfplumber

def extract_text_from_file(file):
    if file.name.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    elif file.name.endswith('.docx'):
        return docx2txt.process(file)
    elif file.name.endswith('.txt'):
        return file.read().decode()
    else:
        return ""

def extract_resume_data(text):
    name = re.findall(r'Name[:\-]?\s*(.*)', text, re.IGNORECASE)
    email = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    phone = re.findall(r'\+?\d[\d -]{8,12}\d', text)
    skills = re.findall(r'Skills[:\-]?\s*(.*)', text, re.IGNORECASE)
    return {
        'name': name[0] if name else '',
        'email': email[0] if email else '',
        'phone': phone[0] if phone else '',
        'skills': skills[0] if skills else ''
    }

def match_keywords(text, keywords):
    found = []
    missing = []
    for keyword in keywords:
        if re.search(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE):
            found.append(keyword)
        else:
            missing.append(keyword)
    return found, missing
