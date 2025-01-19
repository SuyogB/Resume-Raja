import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv


load_dotenv() ## load all our environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(
    page_title="Smart ATS",
    page_icon="🔍",
)

def get_gemini_repsonse(input):
    model=genai.GenerativeModel('gemini-pro')
    response=model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader=pdf.PdfReader(uploaded_file)
    text=""
    for page in range(len(reader.pages)):
        page=reader.pages[page]
        text+=str(page.extract_text())
    return text

#Prompt Template

input_prompt = """
You are an advanced Application Tracking System (ATS) designed to analyze resumes in the context of job descriptions, specifically for tech roles such as software engineering, data science, data analysis, and big data engineering. Your task is to provide a detailed evaluation based on the following criteria, with a score from 1 to 5 (1 being the lowest and 5 being the highest). 

Each of the 9 features should be evaluated separately, and then provide a final **Summary Rating** based on the overall match across all features. Use the star rating system (⭐) corresponding to the score for the 10th feature:

1. **Missing Keywords**: Identify the key skills and keywords mentioned in the job description that are missing from the resume. Provide these in a list.  
2. **Profile Summary**: Provide a summary of the resume in comparison to the job description. Highlight the strengths (skills, experiences, and qualifications that match the JD) and suggest areas of improvement (skills, experiences, or qualifications that are missing or need to be emphasized).  
3. **Skills Match**: List the skills in the job description that are explicitly mentioned in the resume. Rate how well the skills match.  
4. **Experience Level**: Comment on whether the candidate’s experience level (years, role, etc.) matches the requirements in the job description. Is the experience too much, too little, or a good fit?  
5. **Qualifications Check**: Compare the educational qualifications, certifications, or any other required credentials in the job description to those listed on the resume. Are there any critical qualifications missing?  
6. **Format and Structure**: Briefly evaluate if the resume format and structure are appropriate for the job. Does it emphasize the right areas (skills, experience, education, etc.) and make it easy for the recruiter to find key information?  
7. **Soft Skills and Cultural Fit**: Evaluate whether the resume highlights soft skills (like communication, teamwork, problem-solving) and how they align with the job description's cultural or role requirements. Does the resume demonstrate a good cultural fit for the company?  
8. **Technical Skills Depth**: Assess whether the candidate’s technical expertise (e.g., programming languages, software tools, frameworks) matches the level of proficiency required by the job description (basic, intermediate, advanced). Does the resume show sufficient depth of knowledge?  
9. **Language and Clarity**: Evaluate the language used in the resume. Is it clear, professional, and aligned with the tone of the job description? Does the resume present the information in an easy-to-read, concise, and effective way?  

After evaluating all 9 features, provide an overall **Summary Rating** (based on all the features combined) on a scale of 1 to 5. Include the **final star rating** based on the overall match across all these features:

**Final Summary Rating (1-5 stars):** [⭐]  

The output format should be as follows:

- **Missing Keywords:** [List of missing keywords]  
- **Profile Summary:** [Summary of the resume with respect to the job description]  
- **Skills Match:** [Analysis of skills match]  
- **Experience Level:** [Evaluation of experience level]  
- **Qualifications Check:** [Evaluation of qualifications]  
- **Format and Structure:** [Evaluation of resume format]  
- **Soft Skills and Cultural Fit:** [Evaluation of soft skills and cultural fit]  
- **Technical Skills Depth:** [Evaluation of technical skills depth]  
- **Language and Clarity:** [Evaluation of language and clarity]  
- **Final Summary Rating:** [⭐⭐⭐⭐⭐]

Here are a few examples to guide you:

### Example 1:
**Input**
**Resume (text):**  
*"Experienced Software Engineer with expertise in Python, JavaScript, and web development. Strong understanding of databases, cloud technologies, and Agile methodologies."*

**Job Description (jd):**  
*"Looking for a Software Engineer with strong skills in Python, JavaScript, AWS, Docker, and Agile methodologies. Experience in cloud computing and modern web technologies is essential."*

**Expected Output:**
- **Missing Keywords:** AWS, Docker  
- **Profile Summary:** The resume aligns well with the job description in terms of Python, JavaScript, and Agile methodologies. However, the resume does not mention AWS, Docker, or cloud computing, which are key skills for this role.  
- **Skills Match:** The resume demonstrates proficiency in Python, JavaScript, and Agile, which are required for the role. However, AWS and Docker are not mentioned, which are crucial technical skills for the job.  
- **Experience Level:** The experience level appears suitable, but the resume lacks expertise in cloud technologies, which is essential.  
- **Qualifications Check:** The resume does not mention any specific certifications or qualifications in cloud computing or containerization (Docker), which may be missing.  
- **Format and Structure:** The resume has a clear format with emphasis on technical skills and experience. It could benefit from more structured sections dedicated to certifications or specific achievements.  
- **Soft Skills and Cultural Fit:** Soft skills like problem-solving and communication are not clearly stated, which could be beneficial for a role that involves collaboration.  
- **Technical Skills Depth:** The resume demonstrates a good depth of knowledge in Python, JavaScript, and databases but lacks detail on cloud technologies and containerization.  
- **Language and Clarity:** The language is clear and concise, with good use of technical terminology, though it could benefit from more action verbs to describe achievements.  
- **Final Summary Rating:** ⭐⭐⭐⭐

---

### Example 2:
**Input**
**Resume (text):**  
*"Data Scientist with experience in machine learning, data visualization, and statistical analysis. Proficient in Python, R, and SQL. Worked on predictive modeling and big data analysis."*

**Job Description (jd):**  
*"We are looking for a Data Scientist with a background in machine learning, data visualization, Python, SQL, and experience with deep learning frameworks like TensorFlow or PyTorch."*

**Expected Output:**
- **Missing Keywords:** deep learning, TensorFlow, PyTorch  
- **Profile Summary:** The resume highlights strong skills in machine learning, data visualization, Python, and SQL, which match the job description. However, the resume lacks mention of deep learning frameworks like TensorFlow or PyTorch, which are important for this role.  
- **Skills Match:** The resume aligns well with the core skills mentioned in the job description (Python, SQL, machine learning). However, deep learning frameworks are missing, which limits the alignment.  
- **Experience Level:** The experience level is appropriate, but the resume does not specify any experience with deep learning or relevant advanced techniques.  
- **Qualifications Check:** The resume lacks references to advanced qualifications or certifications in deep learning, which might be expected for this role.  
- **Format and Structure:** The format is easy to follow, with clear headings for each section. More emphasis on specific projects or achievements could strengthen the resume.  
- **Soft Skills and Cultural Fit:** Soft skills such as communication or teamwork could be more evident. Cultural fit is not clearly addressed.  
- **Technical Skills Depth:** While the resume demonstrates strong knowledge in data science tools, it lacks depth in deep learning and advanced model-building techniques.  
- **Language and Clarity:** The language is clear and precise, though including more detail on accomplishments and impact would be beneficial.  
- **Final Summary Rating:** ⭐⭐⭐

**Input**
resume: {text}  
description: {jd}

**Output**
"""



## streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS")
jd=st.text_area("Paste the Job Description")
uploaded_file=st.file_uploader("Upload Your Resume",type="pdf",help="Please uplaod the pdf")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text=input_pdf_text(uploaded_file)
        response=get_gemini_repsonse(input_prompt)
        st.subheader(response)