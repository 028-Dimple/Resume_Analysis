from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from docx import Document
import os
import google.generativeai as genai
import shutil
import PyPDF2

app = FastAPI()

genai.configure(api_key="AIzaSyASn1nRtBeZMTOhl3yHxicTloddUEEuKLE")

class QuestionResponse(BaseModel):
    question: str
    answer: str


def extract_text_from_pdf(file_path: str) -> str:
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def generate_questions(resume_text: str) -> list[str]:
    prompt = f"""You are an experienced interviewer. Your task is to generate 10 interview questions based on the following resume text. Follow these rules:
            1. The first question must include the candidate's name (extract it from the resume text).
            2. The remaining 9 questions should be technical, behavioral, or situational questions relevant to the candidate's skills, experience, and qualifications mentioned in the resume.
            3. Ensure the questions are clear, concise, and tailored to the candidate's background.

            Resume Text:
            {resume_text}

            Generate the 10 questions in the following format one in each line:
            1. [First question including the candidate's name]
            2. [Second question]
            3. [Third question]
            ...
            10. [Tenth question]"""
    
    model = genai.GenerativeModel('gemini-1.5-flash-002')
    response = model.generate_content(prompt)
    print("\n\nthis is the response from ai for question: \n", response)
    return response.text.split("\n")


def generate_questions_category_wise(choice: str) -> list[str]:
    prompt = f"""Generate 10 interview questions based on the given topic: "{choice}". The questions should be clear, concise, and relevant to the topic. Format the output with each question on a new line, numbered from 1 to 10.
    Format:

    [Question 1]
    [Question 2]
    [Question 3]
    ...
    [Question 10]
    Ensure that the questions cover fundamental, conceptual, and practical aspects of the topic.
    """
    
    model = genai.GenerativeModel('gemini-1.5-flash-002')
    response = model.generate_content(prompt)
    print("\n\nthis is the response from ai for question: \n", response)
    return response.text.split("\n")



@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File()):
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a PDF or DOCX file.")
    
    # Save the uploaded file as a temporary file in the same directory
    temp_filename = f"temp_resume.{file_extension}"
    with open(temp_filename, "wb") as temp_file:
        shutil.copyfileobj(file.file, temp_file)

    # Process the file based on type
    if file_extension == "pdf":
        text = extract_text_from_pdf(temp_filename)
    else:  # file_extension == "docx"
        text = extract_text_from_docx(temp_filename)

    # Remove the temporary file after processing
    os.remove(temp_filename)

    # Generate questions and return response
    questions = generate_questions(text)
    #questions = ['1. Hemendra, can you walk us through your experience in leading development teams and ensuring project success?', "2. Describe your expertise in building and maintaining Laravel applications, including your experience with the framework's architecture and best practices.", '3. How have you leveraged MEAN Stack in your previous roles, and what were the key outcomes you achieved with this technology stack?', '4. Explain your approach to ensuring code quality and maintaining high standards throughout the software development lifecycle.', '5. How do you stay updated with the latest trends and advancements in the field of web development?', '6. Tell us about a challenging project you worked on that involved complex integrations and how you managed to overcome the technical complexities.', '7. Describe your experience in designing and implementing scalable and efficient database structures, particularly using MySQL.', '8. How do you handle situations where multiple developers are working on the same project? Share your strategies for ensuring collaboration and code coherence.', '9. What are your thoughts on automated testing and how have you implemented it in your previous projects?', '10. Can you elaborate on your experience in optimizing website performance and reducing page load times?']
    print(questions)
    return JSONResponse(content={"questions": questions})



@app.post("/evaluate-answers/")
async def evaluate_answers(responses: list[QuestionResponse]):
    evaluations = []
    total_score = 0.0
    for response in responses:
        # prompt = f"""
        # You are an AI interview evaluator assessing a candidate’s response to an interview question.  
        # Your task is to critically evaluate the given answer based on **relevance, accuracy, depth, clarity, and overall quality**.  

        # ### **Question:**  
        # {response.question}  

        # ### **Candidate's Answer:**  
        # {response.answer}  

        # ---

        # ### **Evaluation Criteria:**  
        # 1. **Relevance** – Does the response directly address the question?  
        # 2. **Accuracy** – Is the information factually and technically correct?  
        # 3. **Depth** – Does the answer demonstrate understanding, experience, and insight?  
        # 4. **Clarity** – Is the answer well-structured, concise, and easy to understand?  
        # 5. **Overall Quality** – How well does the response compare to an ideal answer?  

        # ### **Instructions:**  
        # - Provide a score from 0 to 10, with 0 being poor and 10 being excellent.  
        # - Justify the score with a brief explanation highlighting strengths and areas for improvement.  
        # - Maintain a professional and constructive tone.  


        # ** Provide the evaluation in the format: **
        # Score: X/10

        # Now, evaluate the provided response using the criteria above and generate a score along with a brief, constructive evaluation.
        # """

        prompt = f"""
        You are an AI interview evaluator assessing a candidate’s response to an interview question.  
        Your task is to critically evaluate the given answer based on **relevance, accuracy, depth, clarity, and overall quality**.  

        ### **Question:**  
        {response.question}  

        ### **Candidate's Answer:**  
        {response.answer}  

        ---

        ### **Evaluation Criteria:**  
        1. **Relevance** – Does the response directly address the question?  
        2. **Accuracy** – Is the information factually and technically correct?  
        3. **Depth** – Does the answer demonstrate understanding, experience, and insight?  
        4. **Clarity** – Is the answer well-structured, concise, and easy to understand?  
        5. **Overall Quality** – How well does the response compare to an ideal answer?  

        ### **Instructions:**  
        - Provide a **score from 0 to 10**, with 0 being poor and 10 being excellent.  
        - Justify the score with a brief explanation highlighting strengths and areas for improvement.  
        - Maintain a professional and constructive tone.  


        ** Provide the evaluation in the following format strictly one in each line: **
        Score: X/10
        Feedback: (constructive feedback on the answer)
        Areas for Improvement: (specific suggestions)
        Ideal Answer: (the best possible answer)

        
        Now, evaluate the provided response using the criteria above and generate a score along with a brief, constructive evaluation.
        """

        model = genai.GenerativeModel('gemini-pro')
        evaluation = model.generate_content(prompt)
        print("\n\n The evaluation is: \n\n", evaluation)
        data = evaluation.text.split("\n")
        #data = ['Score: 0/10', "Feedback: The candidate's response is not relevant to the question asked.", 'Areas for Improvement: The candidate should provide a response that describes their experience in designing and implementing scalable and efficient database structures, particularly using MySQL.', 'Ideal Answer: "In my role at [Company A], I was responsible for designing and implementing the database structure for the company\'s new e-commerce website. The website was expected to handle a high volume of traffic, so I used MySQL to create a scalable and efficient database that could meet the demand. I used various techniques to optimize the database, including indexing, partitioning, and caching. The result was a database that could handle the high traffic volume without any performance issues."']
        print("the data is: \n", data)
        score_str = data[0].split(":")[1].split("/")[0].strip()  # Extract '0' as string
        score = float(score_str)
        feedback = data[1].split(":", 1)[1].strip()
        improvement = data[2].split(":", 1)[1].strip()
        ideal_answer = data[3].split(":", 1)[1].strip()
        print("\n\nThe score is: ", score)
        # print("\n\nThe feedback is: ", feedback)
        # print("\n\nThe improvement is: ", improvement)
        # print("\n\nThe ideal answer is: ", ideal_answer)

        evaluations.append({
                "question": response.question,
                "your_answer": response.answer,
                "score": score,
                "feedback": feedback,
                "areas_for_improvement": improvement,
                "ideal_answer": ideal_answer
            })
        total_score = total_score + score
    print("\n\nThe total score is: ", total_score)

    return {"analysis": evaluations, "total_score": total_score}


@app.post("/category/{choice}")
async def category_wise(choice: str):
    #questions = ['1. Describe the different types of financial instruments and their characteristics.', '2. Explain the principles of time value of money and its implications for financial decision-making.', '3. Discuss the role of risk and return in investment analysis.', '4. Describe the different methods used to evaluate the performance of investment portfolios.', '5. Explain the concept of capital budgeting and describe the techniques used to evaluate investment projects.', '6. Discuss the principles of corporate finance, including capital structure, dividend policy, and mergers and acquisitions.', '7. Describe the functions and structure of financial markets, including the primary and secondary markets.', '8. Explain the role of financial intermediaries in the financial system.', '9. Discuss the ethical considerations and regulations that govern financial professionals.', '10. Describe the current trends and challenges facing the financial industry.']
    questions = generate_questions_category_wise(choice)
    print(questions)
    return JSONResponse(content={"questions": questions})
