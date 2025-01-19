import streamlit as st

st.set_page_config(
    page_title="Resume Raja",
    page_icon="👑",
)

st.title("Resume Raja 👑")
st.markdown("### 'Where your Resume Rules!'")

st.sidebar.success("Select a page above.")

st.write('''
Welcome to **Resume Raja**, your ultimate platform to refine, evaluate, and enhance your resume for job applications! With a variety of tools at your disposal, you'll have everything you need to land that perfect job. Here's a quick overview of the features we offer:

### 🔍 Smart ATS (Applicant Tracking System)
Upload your resume and job description (JD), and our system uses advanced AI technology to match the skills listed in your resume with the job requirements. You’ll receive a compatibility score, helping you identify any gaps and improve your chances of success.

### 📝 Spell Checker
Ensure your resume is grammatically perfect! Upload your resume, and our AI will check for grammatical errors, offering suggestions for improvement to make your resume look polished and professional.

### 🎤 Mock Interview
Prepare for your interview like a pro! Upload your resume, job role, and choose the type of interview (Technical or HR). The AI will simulate a interview by asking you 21 questions based on your resume and job role, giving you an edge before the real interview.

### 📥 Upload to Database
Want to add your resume to our database? Upload your resume, and our system will extract all the necessary information.

### 👥 Recruiter Mode
For recruiters, we provide a powerful tool to search and filter resumes. You can view the candidate database and use a chatbot interface to ask the AI questions. The system will help you find candidates that match specific job roles based on the data stored.

---

Each feature is designed to make the resume-building and job application process smoother and more efficient. Whether you're a job seeker or a recruiter, **Resume Raja** has got you covered!
''')

st.write('### 📂 [Source Code](https://github.com/SuyogB/Resume-Raja) | 📄 [User Guide PDF](https://github.com/SuyogB/Resume-Raja/blob/main/User%20Manual.pdf) | 📹 [Video Tutorial](#)')


