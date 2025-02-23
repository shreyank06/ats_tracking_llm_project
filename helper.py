import google.generativeai as genai
from PyPDF2 import PdfReader
import json


def configure_genai(api_key):
    " Configure the Generative AI API with enhanced error handling"
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        raise Exception(f"Error configuring the Generative AI API: {str(e)}")

def get_gemini_response(prompt):
    "Get a response from the Gemini model with error handling"
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        print(f"Response type: {type(response)}")
        print(f"Response content: {response}")


        # Ensure response is not empty
        if not response or not response.text:
            raise Exception("The response from the Gemini model is empty")

        # Try to parse the response as JSON
        try:
            response_json = json.loads(response.text)

            #Validate required fields
            required_fields = ["JD Match", "MissingKeywords", "Profile Summary"]
            for field in required_fields:
                if field not in response_json:
                    raise Exception(f"The response is missing the '{field}' field")

            return response.text

        except json.JSONDecodeError as e:
            # if response is not valid json, try to extract JSON-like content
            import re
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, response.text, re.DOTALL)
            if match:
                return match.group()
            else:
                raise Exception("Could not extract valid JSON response")

    except Exception as e:
        raise Exception(f"Error getting response from the Gemini model: {str(e)}")

def extract_text_from_pdf(uploaded_file):
    "Extract text from a PDF file with error handling"
    try:
        reader = PdfReader(uploaded_file)
        if len(reader.pages) == 0:
            raise Exception("The PDF file is empty")

        text = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)

        if not text:
            raise Exception("The PDF file does not contain any text")

        return " ".join(text)

    except Exception as e:
        raise Exception(f"Error extracting text from the PDF file: {str(e)}")


def prepare_prompt(resume_text, job_description_text):
    print(f"Resume Text: {resume_text[:100]}...")  # Debugging: check input
    print(f"Job Description Text: {job_description_text[:100]}...")  # Debugging: check input

    if not resume_text or not job_description_text:
        raise Exception("The resume text and job description text are empty")

    prompt_template = """
    Act as an expert ATS specialist with deep expertise in:
    - Technical fields
    - Software engineering
    - Data science
    - Data analysis  
    - Big data engineering

    Evaluate the following resume and job description to determine if the candidate is a good fit for the job. Consider that the job market is highly competitive. 
    Provide feedback for resume improvement.

    Resume:
    {resume_text}

    Job Description:
    {job_description_text}

    Provide a response in the following JSON format only:
    {{
        "JD Match": "percentage between 0 and 100",
        "MissingKeywords": ["keyword1", "keyword2", ...],
        "Profile Summary": "detailed analysis of the match and specific improvement suggestions"
    }} 
    """

    formatted_prompt = prompt_template.format(resume_text=resume_text.strip(), job_description_text=job_description_text.strip())
    print(f"Formatted Prompt: {formatted_prompt[:100]}...")  # Debugging: check final formatted prompt
    return formatted_prompt
