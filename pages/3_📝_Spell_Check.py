import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import re

load_dotenv()  # Load environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(
    page_title="Spell Check",
    page_icon="📝",
)

def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_text)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

def clean_text(text):
    """
    Clean the extracted text by removing extra spaces, hyphenated word breaks, unwanted characters,
    and fixing common issues caused by PDF extraction.
    """
    # Remove extra spaces between words and normalize spacing
    text = re.sub(r'\s+', ' ', text)
    
    # Handle common hyphenation cases where words break at the end of lines
    text = re.sub(r'(?<=\w)-\s*(?=\w)', '', text)
    
    # Fix concatenated words due to PDF extraction (e.g., "finetune" becomes "fine-tune")
    # Also handle edge cases like "Proventrackrecord" -> "Proven track record"
    text = re.sub(r'([a-zA-Z])(?=[A-Z])', r'\1 ', text)  # Adds a space before capital letters that follow lowercase
    text = re.sub(r'([a-zA-Z])(?=\d)', r'\1 ', text)  # Adds a space between letters and digits
    
    # Fix common issues with concatenated words from PDF extraction
    text = re.sub(r'(?<=\w)([A-Z])', r' \1', text)  # Fix cases like "Jspider -Training" -> "Jspider - Training"
    text = re.sub(r'([a-zA-Z])([A-Z])', r'\1 \2', text)  # Add space between lowercase and uppercase letters

    # Remove unnecessary spaces before commas, periods, etc.
    text = re.sub(r'\s([,;.!?])', r'\1', text)

    # Fix any case-related issues (e.g., "Jspider -Training & DevelopmentCenter" -> "Jspider - Training & Development Center")
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Fix case transitions

    return text


# Prompt Template
input_prompt_template = """
You are a professional grammar and spell checker AI. Your task is to review the uploaded resume text and ensure it is grammatically correct and professional. You need to:

1. Identify any spelling or grammatical errors in the resume.
2. Provide a list of spelling and grammatical mistakes found in the text.
3. For each error, mention the section of the resume (e.g., Experience, Education, Skills, etc.) where the error is found.
4. Offer suggestions for corrections to improve professionalism, clarity, and readability.
5. Make sure the language used is formal and polished, appropriate for a job application.
6. Provide overall feedback on how the resume can be improved to appear more professional to potential employers.

**Output:**
1. List of spelling and grammatical errors, including where they are found in the resume. (e.g., "abilty" in the Experience section).
2. Suggested corrections for each error, including where they should be applied.
3. General suggestions for improving the professionalism of the resume.

---
For example:
- **Error**: "abilty" (Experience section)
  - **Correction**: "ability"
  - **Suggestion**: Ensure consistency in spelling across the document and verify commonly misspelled words like 'ability'.
  
**Overall Suggestions:**
- Be consistent with verb tense throughout the resume (e.g., past tense for previous roles).
- Use more formal and concise language.
- Consider rephrasing informal phrases to appear more professional.
- Ensure the structure of the resume is clear and well-organized with section headings.

Please make sure that your response only includes the errors that are directly present in the provided resume text, and avoid introducing any other information or assumptions.

The resume text to check is as follows:
**Input**
resume: {text}

**Output**
"""

# Streamlit UI
st.title("Spell Check")
st.text("Check spellings and grammatical errors in your Resume")

uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)  # Extract text from uploaded PDF
        cleaned_text = clean_text(text)  # Clean up the extracted text
        input_prompt = input_prompt_template.format(text=cleaned_text)  # Insert the extracted text into the prompt
        
        response = get_gemini_response(input_prompt)  # Get the response from the generative AI
        st.subheader("Resume Review Results")
        st.write(response)
    else:
        st.error("Please upload a resume PDF file to continue.")
