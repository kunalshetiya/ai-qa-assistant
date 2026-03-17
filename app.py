# AI QA Assistant - Test Case & Edge Case Generator

import os
import tempfile
import logging
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import openai
import docx
import pandas as pd
import fitz

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

ALLOWED_EXTENSIONS = {'pdf', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------ FILE EXTRACTION ------------------

def extract_content_from_pdf(file_path):
    content = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text = page.get_text("text")
            if text:
                content += text + "\n"
    return content


def extract_content_from_docx(file_path):
    doc = docx.Document(file_path)
    content = ""
    for para in doc.paragraphs:
        if para.text.strip():
            content += para.text + "\n"
    return content


# ------------------ AI GENERATION ------------------

def generate_test_cases(input_text):
    logger.info("Generating test cases using OpenAI")

    prompt = f"""
    You are a QA engineer.

    Given the following software requirement:
    {input_text}

    Generate:
    1. Functional test cases
    2. Edge cases including:
       - Boundary values
       - Invalid inputs
       - Security scenarios

    Format output as:
    Test Case ID | Description | Preconditions | Steps | Expected Result
    """

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=2000
    )

    return response.choices[0].message.content.strip()


# ------------------ PARSING ------------------

def parse_test_cases(generated_output):
    test_cases = []
    lines = generated_output.strip().split("\n")

    for line in lines:
        if "|" in line:
            parts = line.split("|")
            if len(parts) >= 5:
                test_cases.append({
                    'Test Case ID': parts[0].strip(),
                    'Description': parts[1].strip(),
                    'Preconditions': parts[2].strip(),
                    'Steps': parts[3].strip(),
                    'Expected Result': parts[4].strip()
                })

    return test_cases


# ------------------ EXPORT ------------------

def write_to_excel(test_cases, filename='output.xlsx'):
    df = pd.DataFrame(test_cases)

    temp_dir = tempfile.gettempdir()
    full_path = os.path.join(temp_dir, filename)

    df.to_excel(full_path, index=False)

    return full_path


# ------------------ ROUTES ------------------

@app.route('/generate-testcases', methods=['POST'])
def generate_ai_testcases():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF and DOCX supported"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(tempfile.gettempdir(), filename)
    file.save(file_path)

    # Extract content
    if filename.endswith('.pdf'):
        content = extract_content_from_pdf(file_path)
    elif filename.endswith('.docx'):
        content = extract_content_from_docx(file_path)
    else:
        return jsonify({"error": "Unsupported file"}), 400

    if not content.strip():
        return jsonify({"error": "No content extracted"}), 400

    # Generate test cases
    generated_output = generate_test_cases(content)

    test_cases = parse_test_cases(generated_output)

    if not test_cases:
        return jsonify({"error": "Failed to generate test cases"}), 500

    file_path = write_to_excel(test_cases)

    return jsonify({
        "message": "Test cases generated successfully",
        "download_url": "/download"
    })


@app.route('/download', methods=['GET'])
def download_file():
    temp_dir = tempfile.gettempdir()
    return send_from_directory(temp_dir, 'output.xlsx', as_attachment=True)


# ------------------ MAIN ------------------

if __name__ == '__main__':
    app.run(debug=True)