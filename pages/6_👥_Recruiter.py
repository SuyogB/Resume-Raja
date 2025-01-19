import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import streamlit as st
import google.generativeai as genai
from langchain_community.vectorstores.faiss import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import pandas as pd
import csv

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(
    page_title="Recruiter",
    page_icon="👥",
)

def read_csv_data(file_path):
    all_data = []  # List to hold all data rows with column names
    
    with open(file_path, 'r', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)  # Extracting the header row
        for row in csv_reader:
            if row:  # Ensuring the row is not empty
                row_data = {headers[i]: row[i] for i in range(len(row))}  # Create a dict with column names
                all_data.append(row_data)

    return all_data  # Return the list of dictionaries

def get_text_chunks(data):
    text = ""
    # Convert list of dictionaries to a structured string
    for entry in data:
        formatted_entry = ' '.join(f"{key}: {value}" for key, value in entry.items())
        text += formatted_entry + "\n"  # Separate entries with newlines

    splitter = RecursiveCharacterTextSplitter(
        separators=['\n'],
        chunk_size=10000, chunk_overlap=1000)
    chunks = splitter.split_text(text)
    return chunks

# get embeddings for each chunk
def get_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001"
    )
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    prompt_template = """
    You are an intelligent and efficient recruiting assistant, designed to help recruiters find the best candidates for job roles.
    You analyze a database of resumes (in CSV format) and provide detailed responses based on job requirements.
    Your role is to assist recruiters in shortlisting candidates for specific roles by matching skills, experience, education,
    and other relevant criteria. When asked a question about a specific candidate, provide the candidate's name directly in the response 
    along with the requested information. If the information is not found, respond clearly with "not found" for that candidate.
    If the question is related to finding the best candidate for a specific role, use the provided data to match the candidates' qualifications
    to the desired job role. If there is no direct match, suggest refining the search criteria or look for additional information in the database.
    Always be professional, helpful, and focused on finding the best match for the recruiter's needs.

    When answering questions, use the following structure:
    - Candidate(s): List of candidates that match the required criteria. \n
    - For specific candidates, provide the response directly with the candidate's name and the requested information. \n
    Example: "John Doe CGPA is 9" or "Jane Doe phone number is not found".
    - If the information is not available, mention "not found". \n
    - Suggested Next Steps: If further information is needed, suggest ways to get the missing data or refine the search. \n
    - Extra Notes: Additional insights related to the candidate or the role.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro",
                                   client=genai,
                                   temperature=0.1,
                                   top_k=10,
                                   )
    prompt = PromptTemplate(template=prompt_template,
                            input_variables=["context", "question"])
    chain = load_qa_chain(llm=model, chain_type="stuff", prompt=prompt)
    
    return chain

def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": "Click on 'Submit & Process' button and ask me a question regarding the candidates."}]

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001")  # type: ignore

    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True) 
    docs = new_db.similarity_search(user_question, top_k=10)

    chain = get_conversational_chain()

    response = chain(
        {"input_documents": docs, "question": user_question}, return_only_outputs=True)

    return response

def run():
    
    st.title("Recruiter Mode")

    file_path = 'resumes_data.csv'
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        st.subheader("Resume Data:")
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='resumes_data.csv',
            mime='text/csv',
        )

        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                raw_text = read_csv_data(file_path)
                text_chunks = get_text_chunks(raw_text)
                if text_chunks:  # Check if text_chunks is not empty
                    get_vector_store(text_chunks)
                    st.success("Done")
                else:
                    st.warning("No data found in CSV file.")

        st.button('Clear Chat History', on_click=clear_chat_history)

        # Chat input
        # Placeholder for chat messages
        if "messages" not in st.session_state.keys():
            st.session_state.messages = [
                {"role": "assistant", "content": "'📥Upload' some Resumes , Click on 'Submit & Process' Button, Ask questions about the candidates "}]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

        # Display chat messages and bot response
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = user_input(prompt)
                    placeholder = st.empty()
                    full_response = ''
                    for item in response['output_text']:
                        full_response += item
                        placeholder.markdown(full_response)
                    placeholder.markdown(full_response)
            if response is not None:
                message = {"role": "assistant", "content": full_response}
                st.session_state.messages.append(message)

    else:
        st.warning("No resume data found.")

run()
