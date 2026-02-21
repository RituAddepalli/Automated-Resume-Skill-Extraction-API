from flask import Flask, request, jsonify
import re
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

app = Flask(__name__)

# =====================================================
# Resume Skill Matcher
# =====================================================

SKILLS = [
    "python", "java", "sql", "mysql", "nosql",
    "html", "css", "data structures", "algorithms",
    "oops", "oop", "spark", "bigquery",
    "hadoop", "aws", "azure", "cloud",
    "docker", "kubernetes", "tensorflow",
    "pytorch", "git", "flask", "ci cd"
]

# Set Tesseract path (if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# =====================================================
# PDF TEXT EXTRACTION
# =====================================================
def extract_text_from_pdf(file):

    file.seek(0)
    text = ""

    try:
        pdf_bytes = file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            extracted = page.get_text("text")
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        print("PyMuPDF extraction failed:", e)

    # OCR fallback
    if not text.strip():
        file.seek(0)
        pdf_bytes = file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_text = pytesseract.image_to_string(img)
            text += ocr_text + "\n"

    text = re.sub(r'[^A-Za-z0-9 ]+', ' ', text).lower()
    return text


# =====================================================
# SKILL MATCHING
# =====================================================
def match_skills(resume_text, target_skills):

    matched = []
    missing = []

    for skill in target_skills:
        if re.search(rf"\b{skill}\b", resume_text, re.IGNORECASE):
            matched.append(skill)
        else:
            missing.append(skill)

    return matched, missing


# =====================================================
# API ENDPOINT
# =====================================================
# @app.route("/analyze", methods=["POST"])
# def analyze_resume():

#     if 'file' not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400
@app.route("/analyze", methods=["POST"])
def analyze_resume():
    print("FILES RECEIVED:", request.files)
    print("FORM RECEIVED:", request.form)

    return jsonify({
        "files_received": list(request.files.keys()),
        "form_received": request.form.to_dict()
    })

    file = request.files['file']

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    target_skills = request.form.get("job_skills")

    if target_skills:
        target_skills = [s.strip().lower() for s in target_skills.split(",")]
    else:
        target_skills = SKILLS

    resume_text = extract_text_from_pdf(file)

    matched, missing = match_skills(resume_text, target_skills)

    return jsonify({
        "message": "Resume Skill Matching Completed",
        "matched_skills": matched,
        "missing_skills": missing
    })


# =====================================================
# HEALTH CHECK
# =====================================================
@app.route("/")
def home():
    return jsonify({"status": "Resume Skill Matcher API is running"})


# =====================================================
# RUN APP
# =====================================================
# if __name__ == "__main__":
#     print("Starting Resume Skill Matcher API...")
#     app.run(debug=True, port=5000)
import os

if __name__ == "__main__":
    print("Starting Resume Skill Matcher API...")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

