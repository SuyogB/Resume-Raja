import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Configure the Generative AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(
    page_title="Mock Interview",
    page_icon="🎤",
)


# Function to get response from the Gemini model
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

# Function to extract text from uploaded PDF resume
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Prompt Template
input_prompt = """
You are an AI assistant that generates interview questions based on the candidate's resume, the job role they are applying for, and the type of interview.

I will provide you with three inputs:
1. Resume: A detailed resume of the candidate, including their education, work experience, projects, internships, certifications, skills, and other relevant qualifications.
2. Job Role: The specific position or job title the candidate is applying for, along with any available job description.
3. Interview Type: The type of interview, which could be either an HR round or a technical round.

Based on this information, generate 21 interview questions:
- If the interview type is **HR**, focus on behavioral and cultural fit questions, communication skills, understanding of the candidate's motivations and career goals, and questions related to their past work experience, internships, and certifications.
- If the interview type is **Technical**, focus on the candidate's technical skills, problem-solving abilities, projects they have worked on, internships, certifications, and knowledge related to the job role and required technologies.

Ensure that the questions are relevant to the candidate's qualifications, including their past experience, projects, internships, and certifications, and avoid generic or unrelated questions.

Now, provide 21 questions for the following inputs:
Resume: {resume}
Job Role: {job_role}
Interview Type: {interview_type}
"""


# Streamlit app
st.title("Mock Interview")
st.text("Can you answer our 21 Questions?")
job_role = st.text_input("Enter Job Role")
interview_type = st.selectbox("Choose Interview Round", ["HR Round", "Technical Round"])

uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the pdf")

submit = st.button("Submit")

# Handle form submission
if submit:
    if uploaded_file is not None:
        # Extract the resume text from the uploaded PDF
        resume_text = input_pdf_text(uploaded_file)

        # Inject the dynamic values into the prompt
        prompt = input_prompt.format(
            resume=resume_text,
            job_role=job_role,
            interview_type=interview_type
        )

        # Get the response from the AI model
        response = get_gemini_response(prompt)
        
        # Display the response in the Streamlit app
        st.subheader("Generated Interview Questions:")
        st.write(response)
