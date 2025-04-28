from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from docx import Document
import os
import google.generativeai as genai
import shutil
import PyPDF2
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem

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
    prompt = f"""You are an experienced interviewer. Your task is to generate 10 interview questions based on the following resume text. Follow these rules strictly:

    1. The first question must include the candidate's name (extract it from the resume text).
    2. The remaining 9 questions should be technical, behavioral, or situational, based on the candidate's skills, experience, and qualifications mentioned in the resume.
    3. Ensure the questions are clear, concise, and directly relevant to the candidate's background.
    4. Do NOT add any blank lines between questions.
    5. Format the output exactly like this, with one question per line:

    1. [First question including the candidate's name]
    2. [Second question]
    3. [Third question]
    ...
    10. [Tenth question]

    Resume Text:
    {resume_text}
    """

    
    model = genai.GenerativeModel('gemini-1.5-flash-002')
    response = model.generate_content(prompt)
    print("\n\nthis is the response from ai for question: \n", response)
    return response.text.split("\n")


def generate_questions_category_wise(choice: str) -> list[str]:
    prompt = f"""Generate 10 interview questions based on the given topic: "{choice}". The questions should be clear, concise, and relevant to the topic. Format the output with each question on a new line, numbered from 1 to 10. Do not leave extra blank line in the end and do not add numbers to the questions.
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
    # questions = generate_questions(text)
    questions = ['1. Hemendra, can you walk us through your experience in leading development teams and ensuring project success?', "2. Describe your expertise in building and maintaining Laravel applications, including your experience with the framework's architecture and best practices.", '3. How have you leveraged MEAN Stack in your previous roles, and what were the key outcomes you achieved with this technology stack?', '4. Explain your approach to ensuring code quality and maintaining high standards throughout the software development lifecycle.', '5. How do you stay updated with the latest trends and advancements in the field of web development?', '6. Tell us about a challenging project you worked on that involved complex integrations and how you managed to overcome the technical complexities.', '7. Describe your experience in designing and implementing scalable and efficient database structures, particularly using MySQL.', '8. How do you handle situations where multiple developers are working on the same project? Share your strategies for ensuring collaboration and code coherence.', '9. What are your thoughts on automated testing and how have you implemented it in your previous projects?', '10. Can you elaborate on your experience in optimizing website performance and reducing page load times?']
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

        model = genai.GenerativeModel('gemini-1.5-flash-002')
        # evaluation = model.generate_content(prompt)
        # print("\n\n The evaluation is: \n\n", evaluation)
        # data = evaluation.text.split("\n")
        data = ['Score: 0/10', "Feedback: The candidate's response is not relevant to the question asked.", 'Areas for Improvement: The candidate should provide a response that describes their experience in designing and implementing scalable and efficient database structures, particularly using MySQL.', 'Ideal Answer: "In my role at [Company A], I was responsible for designing and implementing the database structure for the company\'s new e-commerce website. The website was expected to handle a high volume of traffic, so I used MySQL to create a scalable and efficient database that could meet the demand. I used various techniques to optimize the database, including indexing, partitioning, and caching. The result was a database that could handle the high traffic volume without any performance issues."']
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
    questions = ['1. Describe the different types of financial instruments and their characteristics.', '2. Explain the principles of time value of money and its implications for financial decision-making.', '3. Discuss the role of risk and return in investment analysis.', '4. Describe the different methods used to evaluate the performance of investment portfolios.', '5. Explain the concept of capital budgeting and describe the techniques used to evaluate investment projects.', '6. Discuss the principles of corporate finance, including capital structure, dividend policy, and mergers and acquisitions.', '7. Describe the functions and structure of financial markets, including the primary and secondary markets.', '8. Explain the role of financial intermediaries in the financial system.', '9. Discuss the ethical considerations and regulations that govern financial professionals.', '10. Describe the current trends and challenges facing the financial industry.']
    # questions = generate_questions_category_wise(choice)
    print(questions)
    return JSONResponse(content={"questions": questions})



def enhance_resume_func(resume_text: str, job_description: str):
    prompt = f"""
    You are an expert resume writer and career coach. Your task is to enhance a given resume so that it aligns well with a provided job description.

    Inputs:
    1. resume_text: This is the candidate's current resume.
    2. job_description: This is the job the candidate is applying for.

    Your task:
    - Carefully analyze both the resume and the job description.
    - Identify key skills, qualifications, responsibilities, and keywords from the job description.
    - Improve the resume by:
    - Highlighting relevant experience and skills from the resume that match the job description.
    - Adding missing but relevant skills, tools, or accomplishments that are commonly expected for such a role.
    - Rewriting vague or generic content to be more specific, achievement-focused, and aligned with the job.
    - Making sure the resume is professionally worded, concise, and impactful.

    Rules:
    - Maintain a professional tone and formatting.
    - Do not make up fake work experiences, degrees, or companies.
    - It's acceptable to enhance existing points or infer common responsibilities/tools based on the candidate’s roles.
    - Output the **full improved resume text** only. Do not add explanations or bullet points about changes made.

    Resume Text:
    {resume_text}

    Job Description:
    {job_description}
    """

    model = genai.GenerativeModel('gemini-1.5-flash-002')
    response = model.generate_content(prompt)
    print("\n\nthis is the response from ai for question: \n", response)
    return response.text





def create_pdf_from_text(text: str, output_filename: str):
    """Create a simple black and white PDF resume."""
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=30,
        bottomMargin=30
    )

    # Get the base styles
    styles = getSampleStyleSheet()
    
    # Simple black and white color scheme
    BLACK = colors.HexColor('#000000')
    
    # Define professional styles
    styles.add(ParagraphStyle(
        name='MainName',
        parent=styles['Heading1'],
        fontSize=16,
        spaceBefore=0,
        spaceAfter=2,
        textColor=BLACK,
        alignment=0,  # Left alignment
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='SubTitle',
        parent=styles['BodyText'],
        fontSize=11,
        spaceBefore=0,
        spaceAfter=12,
        textColor=BLACK,
        alignment=0,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=15,
        spaceAfter=6,
        textColor=BLACK,
        fontName='Helvetica-Bold',
        alignment=0
    ))
    
    styles.add(ParagraphStyle(
        name='NormalText',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=BLACK,
        alignment=0,
        leading=14,
        spaceBefore=1,
        spaceAfter=1,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='BoldText',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=BLACK,
        alignment=0,
        leading=14,
        spaceBefore=1,
        spaceAfter=1,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='ContactInfo',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=BLACK,
        alignment=0,
        leading=14,
        spaceBefore=1,
        spaceAfter=1,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='BulletPoint',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=BLACK,
        leading=14,
        leftIndent=15,
        bulletIndent=9,
        spaceBefore=1,
        spaceAfter=1,
        fontName='Helvetica'
    ))

    # Story (content)
    story = []
    current_section = None
    
    # Process the content
    sections = text.split('\n\n')
    for section in sections:
        if not section.strip():
            continue
            
        lines = section.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Handle section headers
            if line.startswith('**') and line.endswith('**'):
                current_section = line.strip('*').strip()
                if current_section.upper() == 'NAME':
                    continue
                story.append(Paragraph(current_section.upper(), styles['SectionHeader']))
                continue
            
            # Handle name section
            if current_section and current_section.upper() == 'NAME':
                if 'Data Scientist' in line or 'Python Developer' in line:
                    story.append(Paragraph(line, styles['SubTitle']))
                elif not any(x in line.lower() for x in ['phone:', 'email:', 'linkedin:']):
                    story.append(Paragraph(line, styles['MainName']))
                continue
            
            # Handle contact information
            if current_section and current_section.upper() == 'CONTACT INFORMATION':
                story.append(Paragraph(line, styles['ContactInfo']))
                continue
            
            # Handle bullet points and regular content
            if line.startswith('*') or line.startswith('-') or line.startswith('•'):
                text = line.lstrip('*-• ').strip()
                # Check if the line contains project or technology keywords to bold
                if any(keyword in text for keyword in ['Project-', 'Python', 'Django', 'Flask', 'FastAPI', 'ML', 'AI']):
                    parts = text.split(':')
                    if len(parts) > 1:
                        story.append(Paragraph(f"• <b>{parts[0]}</b>: {parts[1]}", styles['BulletPoint']))
                    else:
                        story.append(Paragraph(f"• {text}", styles['BulletPoint']))
                else:
                    story.append(Paragraph(f"• {text}", styles['BulletPoint']))
            else:
                # Check if line contains a year or date pattern to make it bold
                if any(str(year) in line for year in range(2000, 2025)):
                    story.append(Paragraph(f"<b>{line}</b>", styles['NormalText']))
                else:
                    story.append(Paragraph(line, styles['NormalText']))
    
    try:
        doc.build(story)
    except Exception as e:
        raise ValueError(f"Error building PDF: {str(e)}")


def generate_score(resume_text: str, job_description: str):
    prompt = f"""
    You are an experienced recruiter and career advisor. Your task is to evaluate how well a candidate's resume matches a given job description.

    Inputs:
    1. resume_text: This is the candidate's current resume.
    2. job_description: This is the job the candidate is applying for.

    Your task:
    - Carefully read both the resume and the job description.
    - Assess how closely the resume matches the job description based on:
        - Relevant skills and technical expertise
        - Educational background
        - Work experience and accomplishments
        - Use of important keywords and tools mentioned in the job description
        - Overall alignment with the role's responsibilities and requirements

    Scoring:
    - Assign a score out of 100, where:
        - 90-100: Excellent match
        - 75-89: Good match
        - 50-74: Moderate match
        - Below 50: Poor match

    Rules:
    - Be strict but fair while scoring. 
    - Do not assume skills or experiences that are not mentioned in the resume.
    - If important skills, qualifications, or experience are missing or weakly presented, reduce the score accordingly.
    - Base your evaluation purely on the provided information.

    Return the output in the following JSON format:
    {{
    "score": [score out of 100]
    }}
    Resume Text:
    {resume_text}

    Job Description:
    {job_description}
    """

    model = genai.GenerativeModel('gemini-1.5-flash-002')
    response = model.generate_content(prompt)
    print("\n\nthis is the response from ai for question: \n", response)
    return response.text



@app.post("/enhance-resume")
async def enhance_resume(job_description: str = Form(...), file: UploadFile = File(...)):
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
    os.remove(temp_filename)  # Ensure the file is removed only once

    enhanced_filename = f"enhanced_resume_{os.urandom(4).hex()}"

    # Generate enhanced resume
    enhanced_text = """KARTIKEYA KUMAR
        Email: kartikeyakumar143@gmail.com                                               Mobile: 8168970525

        **Summary**

        Highly motivated and results-oriented Machine Learning and Automation Engineer with 3+ years of experience in designing, developing, and deploying ML models for process automation and predictive analytics within the telecom industry. Proven ability to leverage Python, NLP, and RPA (UiPath, Automation Anywhere) to enhance operational efficiency, reduce costs, and improve decision-making.  Seeking to contribute expertise in AI/ML model development and deployment to a challenging and innovative environment.  Currently pursuing a Master of Science in Data Science.

        **Experience**

        **Ericsson India Global Services Private Limited**  | March 2022 – Present
        **Automation Engineer**

        * Spearheaded the development of an NLP-powered intent classification system using Sentence Transformers, automating network checks and reducing manual effort by [quantify percentage or time saved].
        * Developed and deployed a high-accuracy (87%) ML model to predict telecom tower failures, leveraging weather data, maintenance records, and power consumption to optimize downtime and reduce associated costs by [quantify percentage or dollar amount].
        * Designed and implemented Python-based ETL pipelines processing 3G/4G/5G network logs, transforming and loading structured data into a database.  Automated log management significantly improved data processing speed and reliability.
        * Automated deep sleep mode activation for 5G signal nodes, resulting in a [quantify percentage] reduction in energy consumption during low-traffic periods while maintaining optimal network performance.
        * Engineered UiPath RPA workflows to automate voucher processing from Outlook emails, integrating with a database and visualizing trends using Tableau. Achieved an 80% reduction in manual effort.

        **Circulant Software Pvt. Ltd.** | October 2021 – March 2022
        **RPA Intern**
        * [Describe key accomplishments and quantifiable results during internship, focusing on relevant skills like RPA workflow design and automation.]

        **Ericsson India Global Services Private Limited** | January 2021 – June 2021
        **Python Intern**
        * [Describe key accomplishments and quantifiable results during internship, focusing on relevant skills like data processing, scripting, and Python programming.]


        **Skills**

        * **Programming Languages:** Python (Pandas, NumPy, Scikit-learn, Matplotlib), SQL
        * **Machine Learning:** Model building, deployment, performance monitoring, A/B testing, predictive modeling, NLP (Sentence Transformers)
        * **RPA:** UiPath (workflow design, development, deployment), Automation Anywhere
        * **Databases:** MySQL
        * **Data Visualization:** Tableau, Power BI
        * **Tools & Platforms:** Docker, Jupyter Notebook, Visual Studio Code, Linux


        **Education**

        **Master of Science (Data Science)** | 2023 – 2025 (Expected Graduation)
        BITS Pilani, Pilani, India

        **Bachelor of Technology (Computer Science Engineering)** | 2017 – 2021
        JECRC University, Jaipur, India

        **Certifications**

        * UiPath RPA Developer Foundation
        * UiPath RPA Citizen Developer
        * Automation Anywhere Advanced RPA Professional
        * Automation Anywhere Essentials RPA Professional
        * BCSS – Automation Experiences Level (Ericsson)
        * BCSS – Machine Learning Fundamental Level (Ericsson)"""
    
    output_filename = enhanced_filename + ".pdf"

    create_pdf_from_text(enhanced_text, output_filename)

# Generate score
    # score = generate_score(enhanced_text, job_description)
    score = {"score": 70}
    print("The score is: ", score)

    return {
        "file_path": output_filename,
        "score": score["score"]
        }

