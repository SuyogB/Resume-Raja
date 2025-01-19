import streamlit as st
import os
import pandas as pd
import json
import PyPDF2 as pdf
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the API key for Google Gemini model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(
    page_title="Upload",
    page_icon="📥",
)

# Function to get response from Gemini model
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

# Function to extract text from uploaded PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Function to retry the extraction process up to 3 times
def extract_resume_info_with_retries(resume_text, max_attempts=3):
    for attempt in range(1, max_attempts + 1):
        st.write(f"Attempt {attempt} to extract information...")

        # Prepare the system prompt
        input_prompt = f"""
    You are an AI assistant tasked with extracting specific information from a resume. The resume text is provided below, and you are required to find the following fields and provide the details in a structured JSON format. If a field is not found, respond with "Not found" for that field. Please make sure that the output strictly follows the required fields. Do not include any extra information or fields. Ensure that the values are populated correctly, and there are no duplicates or missing fields.

    Here are the fields:

        1) Full Name: The name is usually at the top of the resume and may be formatted in bold or larger text. It is often followed by contact information such as an email or phone number. Look for words that are proper nouns (capitalized) and exclude titles like 'Mr.', 'Ms.', etc.

        2) Contact details (Email, Phone Number): Find the email address and phone number as they appear in the resume.

        3) University/College: Look for the educational institution name, typically found in the 'Education' or 'Academic Background' section.

        4) Year of Study: This can be a date range (e.g., 2018-2022) or a single year if the person is currently studying.

        5) Course/Program: The name of the course or program being pursued.

        6) Discipline/Major: The field of study or specialization.

        7) CGPA/Percentage: Academic score, typically labeled as 'CGPA' or 'GPA', or percentage.

        8) Key Skills: Any specific skills mentioned in the resume. Look for sections labeled 'Skills' or 'Core Competencies'.

        9) Gen AI Experience Score: Provide a score based on experience mentioned in Gen AI. The score should be on a scale from 1 to 3, where:
            - 1 means Exposed (has knowledge or exposure to Gen AI concepts but no hands-on experience).
            - 2 means Hands-on (has worked on Gen AI projects but without advanced techniques).
            - 3 means Advanced (has worked on advanced areas of Gen AI such as Agentic RAG, Evals, etc.).

        10) AI/ML Experience Score: Provide a score based on experience mentioned in AI or Machine Learning. The score should be on a scale from 1 to 3, where:
            - 1 means Exposed (has knowledge or exposure to AI/ML concepts but no hands-on experience).
            - 2 means Hands-on (has worked on AI/ML projects but without advanced techniques).
            - 3 means Advanced (has worked on advanced areas of AI/ML such as deep learning, reinforcement learning, etc.).

        11) Supporting Information (Certifications, Internships, Projects): Any certifications, internships, or projects relevant to the field.

        **Important Notes**:
        - The values for each field must be **accurate** and **appear only once**.
        - If a field does not exist in the resume, return **"Not found"** for that field.
        - Make sure there are **no duplicates**
        - Do not include any unnecessary fields or information. Only return the required fields in the format specified below:

        Return the result in **valid JSON format** only. Do not include any extra text or explanations.

        Extract the information only from this resume content:
        "{resume_text}"
        """

        # Get the response from the Gemini LLM
        response = get_gemini_response(input_prompt)

        # Debug the response
        st.write("Raw Gemini Response:", response)  # Print out raw response for debugging

        # Clean up the response to extract the JSON part
        json_start = response.find('{')
        json_end = response.rfind('}')
        
        if json_start != -1 and json_end != -1:
            clean_response = response[json_start:json_end+1]  # Extract the JSON part
        else:
            st.error("Couldn't find JSON in the response.")
            return ""  # Exit early if no valid JSON

        try:
            extracted_data = json.loads(clean_response)  # Safely parse the cleaned JSON

            # Validate that the 'Full Name' exists and is not 'Not found'
            if extracted_data.get('Full Name') and extracted_data['Full Name'] != 'Not found':
                return extracted_data  # Return only if name is valid
            else:
                st.warning("No valid 'Full Name' found in the resume. Skipping entry.")
                return ""  # Return empty if name is missing or invalid
        except json.JSONDecodeError:
            st.error("Invalid JSON format in the extracted data.")
            return ""  # Return an empty string if parsing fails

# Function to update CSV with extracted resume data
def update_resume_csv(data_dict):
    # Check if 'Full Name' is found, if not skip adding to CSV
    full_name = data_dict.get('Full Name', 'Not found')
    if full_name == 'Not found':
        st.warning("No valid 'Full Name' found in the resume. Skipping entry.")
        return None  # Skip further processing if name is not found


    # File path of the CSV file
    csv_file = 'resumes_data.csv'

    # Ensure 'Key Skills' is a string (if it's a list, join it into a string)
    if isinstance(data_dict.get('Key Skills'), list):
        data_dict['Key Skills'] = ', '.join(data_dict['Key Skills'])  # Join list elements as a string

    # Check if CSV file exists
    if os.path.exists(csv_file):
        # Load existing data
        df = pd.read_csv(csv_file)
    else:
        # If file doesn't exist, create an empty DataFrame with required columns
        df = pd.DataFrame(columns=[ 
            'Full Name', 'Contact details', 'University/College', 'Year of Study',
            'Course/Program', 'Discipline/Major', 'CGPA/Percentage', 'Key Skills',
            'Gen AI Experience Score', 'AI/ML Experience Score', 'Supporting Information'
        ])

    # Convert 'Full Name' column and the new name to lowercase for case-insensitive comparison
    name_in_csv = df['Full Name'].str.lower()
    name_in_dict = data_dict['Full Name'].lower()

    # Check if the name already exists in the CSV (case-insensitive)
    if name_in_dict in name_in_csv.values:
        # Update the corresponding row (case-insensitive match)
        index_to_update = name_in_csv[name_in_csv == name_in_dict].index[0]
        df.loc[index_to_update, :] = pd.Series(data_dict)
    else:
        # Append the new row to the DataFrame
        new_row = pd.DataFrame([data_dict])
        df = pd.concat([df, new_row]).reset_index(drop=True)

    # Save the updated CSV file
    df.to_csv(csv_file, index=False)

    return df


def run():
    st.title("Resume Extractor with CSV Output")
    st.text("Upload resume(s) to extract and save information to CSV.")
    
    
    uploaded_files = st.file_uploader("Upload Your Resumes", type="pdf", accept_multiple_files=True, help="Upload multiple PDF resumes.")
    submit = st.button("Submit")

    if submit:
        if uploaded_files:
            for uploaded_file in uploaded_files:
                resume_text = input_pdf_text(uploaded_file)

                if resume_text.strip():
                    extracted_info = extract_resume_info_with_retries(resume_text, max_attempts=3)

                    if extracted_info:  # Check if data was extracted
                        df = update_resume_csv(extracted_info)
                        if df is not None:
                            st.success("Resume information extracted and saved. Check '👥 Recruiter' mode.")
                        else:
                            st.warning("No valid data extracted, skipping entry.")
                else:
                    st.error("The text extracted from the uploaded PDF is empty. Please upload a valid resume file.")


run()
