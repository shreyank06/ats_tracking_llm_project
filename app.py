import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import os
import json
from dotenv import load_dotenv
from helper import get_gemini_response, extract_text_from_pdf, prepare_prompt, configure_genai

def init_session_state():
    "Initialize session state variables"
    if 'processing' not in st.session_state:
        st.session_state.processing = False

def main():
    # Load environment variables
    load_dotenv()

    # Initialize session state variables
    init_session_state()

    # Configure Generative AI
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Please set the GOOGLE_API_KEY environment variable")
        return  

    try:
        configure_genai(api_key)
    except Exception as e:
        st.error(f"Error configuring the Generative AI API: {str(e)}")
        return

    # Sidebar
    with st.sidebar:
        st.title("Smart ATS")
        st.subheader("About")
        st.write("""
        This smart ATS helps you:
        - Evaulate resume-job description match
        - Identify missing keywords
        - Get personalized improvement suggestions
        """)

    # Main content
    st.title("Smart ATS Resume Analyzer")
    st.subheader("Optimize your resume for ATS")

    # Input sections with validation

    jd = st.text_area(
        "Job Description",
        placeholder="Paste the job description here",
        help="Enter the complete job description for accurate analysis"
    )

    uploaded_file = st.file_uploader(
        "Resume (PDF)",
        type=["pdf"],
        help="Upload your resume in PDF format"
    )

    # Process button with loading state
    if st.button(" Analyze Resume", disabled=st.session_state.processing):
        if not jd:
            st.warning("Please enter the job description")
            return

        if not uploaded_file:
            st.warning("Please upload your resume in PDF format")

        st.session_state.processing = True

        try:
            with st.spinner("Analyzing resume..."):
                # Extract text from PDF
                resume_text = extract_text_from_pdf(uploaded_file)
                #print(f"Extracted Resume Text: {resume_text[:100]}...")  # Check the extracted resume text
                #print(f"Job description text: {jd[:200]}...")  # Print first 100 characters of job_description_text

                # Prepare prompt
                prompt = prepare_prompt(resume_text, jd)

                # Get response from Gemini model
                response = get_gemini_response(prompt)
                response_json = json.loads(response)

                # Display results
                st.success("Resume analyzed successfully")

                # Match percentage
                match_percentage = response_json.get("JD Match", "N/A")
                st.metric("Match Percentage", f"{match_percentage}%", "This is the percentage match between your resume and the job description")
                
                # Missing keywords
                st.subheader("Missing Keywords")
                missing_keywords = response_json.get("MissingKeywords", [])
                if missing_keywords:
                    st.write(", ".join(missing_keywords))
                else:
                    st.info("No missing keywords found")    

                # Profile summary
                st.subheader("Profile Summary")
                st.write(response_json.get("Profile Summary", "No profile summary found"))

        except Exception as e:
            st.error(f"Error analyzing resume: {str(e)}")

        finally:
            st.session_state.processing = False

if __name__ == "__main__":
    main()