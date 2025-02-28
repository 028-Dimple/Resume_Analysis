import streamlit as st 
import requests

BACKEND_URL = "http://localhost:8000"

def next_question():
    if st.session_state.current_question < len(st.session_state.questions) - 1:
        st.session_state.current_question += 1

def prev_question():
    if st.session_state.current_question > 0:
        st.session_state.current_question -= 1


st.title("Practice for Interview")

st.write("Hi, I’m Jesse, your personal assistant. I’m here to help you practice interviews and land your dream job.")
st.write("Would you like to start by uploading Resume?")

if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}

selection = st.radio(label = "Select one", options = ["Yes, Upload my resume", "No, I will skip this step"], index = None)

if selection == "Yes, Upload my resume":
    uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx", "doc"])
    if uploaded_file is not None and not st.session_state.questions:
        if st.button(label = "Start Interview"):
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
            key=f"answer_{current_index}"
        )
        st.session_state.responses[current_index] = answer

        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("Previous", on_click=prev_question, disabled=current_index == 0)
        with col2:
            st.button("Next", on_click=next_question, disabled=current_index == len(st.session_state.questions) - 1)
        with col3:
            if current_index == len(st.session_state.questions) - 1:
                if st.button("Submit"):
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



if selection == "No, I will skip this step":
    st.write("Choose the job category you'd like to interview for: ")
    if not st.session_state.questions:
        choice = st.radio("choose one", options = ["Healthcare", "Technology", "Finance", "customer service"], index = None)
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
            key=f"answer_{current_index}"
        )   

        st.session_state.responses[current_index] = answer

        col1, col2, col3 = st.columns(3)

        with col1:
            st.button("Previous", on_click=prev_question, disabled=current_index == 0)
        with col2:
            st.button("Next", on_click=next_question, disabled=current_index == len(st.session_state.questions) - 1)

        with col3:
            if current_index == len(st.session_state.questions) - 1:
                if st.button("Submit"):
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