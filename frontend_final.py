import streamlit as st 
import requests
import os  # Import os module for file removal

BACKEND_URL = "http://localhost:8000"


if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}

def next_question():
    if st.session_state.current_question < len(st.session_state.questions) - 1:
        st.session_state.current_question += 1

def prev_question():
    if st.session_state.current_question > 0:
        st.session_state.current_question -= 1


def mock_interview():
    st.session_state.show_mock_interview = True

def render_mock_interview():
    if not st.session_state.questions:
        uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx", "doc"])
        if uploaded_file is not None:
            if st.button(label="Start Interview", key="start_mock_interview"):  # Added unique key
                with open("temp_resume." + uploaded_file.name.split(".")[-1], "wb") as f:
                    f.write(uploaded_file.getbuffer())
                response = requests.post(
                    f"{BACKEND_URL}/upload-resume/",
                    files={"file": open("temp_resume." + uploaded_file.name.split(".")[-1], "rb")}
                )
                if response.status_code == 200:
                    st.session_state.questions = response.json().get("questions", [])
                    st.session_state.current_question = 0
                    st.session_state.responses = {i: "" for i in range(len(st.session_state.questions))}
                    st.rerun()

    if st.session_state.questions:
        current_index = st.session_state.current_question
        question = st.session_state.questions[current_index]

        st.write(f"**Question {current_index + 1}:** {question}")

        if current_index not in st.session_state.responses:
            st.session_state.responses[current_index] = ""

        answer = st.text_area(
            "Your Answer",
            value=st.session_state.responses[current_index],
            key=f"mock_answer_{current_index}"  # Updated key to include "mock"
        )
        st.session_state.responses[current_index] = answer

        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("Previous", on_click=prev_question, disabled=current_index == 0, key=f"mock_prev_{current_index}")  # Added unique key
        with col2:
            st.button("Next", on_click=next_question, disabled=current_index == len(st.session_state.questions) - 1, key=f"mock_next_{current_index}")  # Added unique key
        with col3:
            if current_index == len(st.session_state.questions) - 1:
                if st.button("Submit", key="submit_mock_interview"):  # Added unique key
                    responses = [{"question": q, "answer": st.session_state.responses[i]} for i, q in enumerate(st.session_state.questions)]
                    evaluation_response = requests.post(f"{BACKEND_URL}/evaluate-answers/", json=responses)

                    if evaluation_response.status_code == 200:
                        result = evaluation_response.json()
                        st.session_state.analysis = result["analysis"]
                        st.session_state.total_score = result["total_score"]
                        st.session_state.show_results = True
                        st.rerun()
                    else:
                        st.error("Failed to evaluate answers.")

    if "show_results" in st.session_state and st.session_state.show_results:
        st.success(f"Your Total Score: {st.session_state.total_score} / 100")
        st.subheader("Detailed Analysis Report")
        for evaluation in st.session_state.analysis:
            st.write(f"**Question:** {evaluation['question']}")
            st.write(f"**Your Answer:** {evaluation['your_answer']}")
            st.write(f"**Score:** {evaluation['score']}/10")
            st.write(f"**Feedback:** {evaluation['feedback']}")
            st.write(f"**Areas for Improvement:** {evaluation['areas_for_improvement']}")
            st.write(f"**Ideal Answer:** {evaluation['ideal_answer']}")
            st.markdown("---")


def category_interview():
    st.session_state.show_category_interview = True

def render_category_interview():
    if not st.session_state.questions:
        st.write("Choose the job category you'd like to interview for: ")
        choice = st.radio("Choose one", options=["Healthcare", "Technology", "Finance", "Customer Service"], index=None)
        if st.button("Start Interview", key="start_category_interview"):  # Added unique key
            response = requests.post(f"{BACKEND_URL}/category/{choice}")
            if response.status_code == 200:
                st.session_state.questions = response.json().get("questions", [])
                st.session_state.current_question = 0
                st.session_state.responses = {i: "" for i in range(len(st.session_state.questions))}
                st.rerun()

    if st.session_state.questions:
        current_index = st.session_state.current_question
        question = st.session_state.questions[current_index]
        st.write(f"**Question {current_index + 1}:** {question}")

        if current_index not in st.session_state.responses:
            st.session_state.responses[current_index] = ""

        answer = st.text_area(
            "Your Answer",
            value=st.session_state.responses[current_index],
            key=f"category_answer_{current_index}"  # Updated key to include "category"
        )

        st.session_state.responses[current_index] = answer

        col1, col2, col3 = st.columns(3)

        with col1:
            st.button("Previous", on_click=prev_question, disabled=current_index == 0, key=f"category_prev_{current_index}")  # Added unique key
        with col2:
            st.button("Next", on_click=next_question, disabled=current_index == len(st.session_state.questions) - 1, key=f"category_next_{current_index}")  # Added unique key
        with col3:
            if current_index == len(st.session_state.questions) - 1:
                if st.button("Submit", key="submit_category_interview"):  # Added unique key
                    responses = [{"question": q, "answer": st.session_state.responses[i]} for i, q in enumerate(st.session_state.questions)]
                    evaluation_response = requests.post(f"{BACKEND_URL}/evaluate-answers/", json=responses)

                    if evaluation_response.status_code == 200:
                        result = evaluation_response.json()
                        st.session_state.analysis = result["analysis"]
                        st.session_state.total_score = result["total_score"]
                        st.session_state.show_results = True
                        st.rerun()

                    else:
                        st.error("Failed to evaluate answers.")

    if "show_results" in st.session_state and st.session_state.show_results:
        st.success(f"Your Total Score: {st.session_state.total_score} / 100")
        st.subheader("Detailed Analysis Report")
        for evaluation in st.session_state.analysis:
            st.write(f"**Question:** {evaluation['question']}")
            st.write(f"**Your Answer:** {evaluation['your_answer']}")
            st.write(f"**Score:** {evaluation['score']}/10")
            st.write(f"**Feedback:** {evaluation['feedback']}")
            st.write(f"**Areas for Improvement:** {evaluation['areas_for_improvement']}")
            st.write(f"**Ideal Answer:** {evaluation['ideal_answer']}")
            st.markdown("---")


def enhance_resume():
    st.session_state.show_enhance_resume = True

def render_enhance_resume():
    if "resume_uploaded" not in st.session_state:
        st.session_state.resume_uploaded = False

    if not st.session_state.resume_uploaded:
        uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx", "doc"])
        if uploaded_file is not None:
            with open("temp_resume." + uploaded_file.name.split(".")[-1], "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.resume_file_path = "temp_resume." + uploaded_file.name.split(".")[-1]
            st.session_state.resume_uploaded = True
            st.session_state.uploaded_file_extension = uploaded_file.name.split(".")[-1]  # Save file extension in session state
            st.rerun()

    if st.session_state.resume_uploaded:
        st.write("Enter Job description")
        job_description = st.text_area("Job Description", height=200)
        if job_description:
            if st.button(label="Enhance Resume", key="enhance_resume"):  # Added unique key
                with open(st.session_state.resume_file_path, "rb") as resume_file:
                    files = {"file": resume_file}
                    data = {"job_description": job_description}
                    response = requests.post(
                        f"{BACKEND_URL}/enhance-resume/",
                        files=files,
                        data=data
                    )

                if response.status_code == 200:
                    st.download_button(
                        label="Download Enhanced Resume",
                        data=response.content,
                        file_name="enhanced_resume." + st.session_state.uploaded_file_extension,  # Use saved file extension
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                    st.success("Your resume has been enhanced! Click the button above to download it.")
                    
                    # Remove the temporary file after download
                    if os.path.exists(st.session_state.resume_file_path):
                        os.remove(st.session_state.resume_file_path)
                else:
                    st.error(f"Failed to enhance resume. Error: {response.status_code}")


st.title("Practice for Interview")

st.write("Hi, I’m Jesse, your personal assistant. I’m here to help you practice interviews and land your dream job.")

st.write("Select one option: ")

col1, col2, col3 = st.columns(3)

with col1:
    st.button("Enhance Resume", on_click=enhance_resume, key="enhance_resume_button")  # Added unique key
with col2:
    st.button("Mock Interview", on_click=mock_interview, key="mock_interview_button")  # Added unique key
with col3:
    st.button("Category based Mock Interview", on_click=category_interview, key="category_interview_button")  # Added unique key

if "show_mock_interview" in st.session_state and st.session_state.show_mock_interview:
    render_mock_interview()

if "show_category_interview" in st.session_state and st.session_state.show_category_interview:
    render_category_interview()

if "show_enhance_resume" in st.session_state and st.session_state.show_enhance_resume:
    render_enhance_resume()


