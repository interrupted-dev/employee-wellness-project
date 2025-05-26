import streamlit as st
import json
import requests 
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]


GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


questions = {
    "Sales": [
        "How clear and communicated are the overall company sales goals?",
        "How satisfied are you with the lead generation process and quality?",
        "How effective is the sales training and onboarding you received?",
        "Do you feel empowered to make decisions that benefit your sales efforts?",
        "How would you rate the tools and technologies provided for sales activities (e.g., CRM)?",
        "How often do you receive constructive feedback on your sales performance?",
        "How well do you feel your work-life balance is in this sales role?",
        "Do you believe there are sufficient opportunities for advancement within the sales team?",
        "How valued do you feel your contributions are to the overall success of the company?",
        "How open is the communication between the sales team and other departments?",
    ],
    "Marketing": [
        "How aligned do you feel your individual goals are with the overall marketing strategy?",
        "How effective do you believe the processes are for campaign development and execution?",
        "How satisfied are you with the level of collaboration within the marketing team?",
        "Do you feel you have the autonomy to explore innovative marketing approaches?",
        "How would you rate the resources available for professional development in marketing?",
        "How clear is the feedback process on your marketing initiatives and performance?",
        "How manageable do you find your workload in your current marketing role?",
        "Do you see clear pathways for career progression within the marketing department?",
        "How recognized do you feel for your creative contributions and marketing successes?",
        "How well do you understand the impact of your marketing work on the company's bottom line?",
    ],
    "Engineering": [
        "How well-defined are the project requirements and specifications you work on?",
        "How effective do you believe the code review processes are within your team?",
        "How satisfied are you with the opportunities to work with new technologies?",
        "Do you feel your input is valued in technical decision-making processes?",
        "How would you rate the quality of the tools and software you use for development?",
        "How often do you receive feedback on your technical skills and contributions?",
        "How sustainable do you find the pace and workload of your engineering projects?",
        "Are you aware of opportunities for specialization or leadership within the engineering organization?",
        "How much do you feel your technical expertise contributes to the company's innovation?",
        "How effective is the communication between engineering teams and other departments (e.g., product)?",
    ],
    "Human Resources": [
        "How effectively do you believe the company's values are reflected in HR practices?",
        "How satisfied are you with the tools and systems used for HR management?",
        "How well do you feel employee grievances and concerns are addressed?",
        "Do you believe the performance evaluation process is fair and constructive?",
        "How would you rate the support provided by HR leadership and management?",
        "How clear is the communication regarding changes in company policies and procedures?",
        "How manageable do you find the workload associated with your HR responsibilities?",
        "Do you see opportunities for growth and specialization within the HR function?",
        "How valued do you feel your role is in supporting the overall employee experience?",
        "How effective is the collaboration between different teams within the HR department?",
    ],
    "Finance": [
        "How clear and consistent are the financial reporting deadlines and expectations?",
        "How satisfied are you with the opportunities to develop your financial analysis skills?",
        "How effective do you believe the internal controls are within the finance department?",
        "Do you feel you have sufficient access to the data and information needed for your work?",
        "How would you rate the quality of the financial software and systems you use?",
        "How often do you receive feedback on the accuracy and efficiency of your work?",
        "How demanding do you find the workload during peak financial periods?",
        "Are you aware of opportunities for advancement or specialization within the finance team?",
        "How much do you feel your financial insights contribute to the company's strategic decisions?",
        "How effective is the communication between the finance department and other departments?",
    ],
}


def get_gemini_recommendations(department: str, ratings: dict) -> tuple[list, str]:
    """
    Calls the Gemini API to get retention recommendations and a summary
    based on employee ratings, with a word limit.

    Args:
        department (str): The department name for context.
        ratings (dict): A dictionary where keys are questions and values are
                        the employee's ratings (1-5).

    Returns:
        tuple[list, str]: A tuple containing a list of bullet-point recommendations
                          (strings) and a summary string. Returns error messages
                          in the list if the API call fails.
    """
   
    prompt_text = f"""
    An employee from the {department} department has provided feedback on their wellness and satisfaction.
    Their ratings (1=Strongly Disagree, 5=Strongly Agree) are as follows:

    """
    
    for question, rating in ratings.items():
        prompt_text += f"- **{question}**: {rating}/5\n"

    prompt_text += f"""

    Based on these ratings, please provide specific, actionable recommendations in bullet points
    to help retain this employee and improve their well-being within the {department} department.
    Focus on areas where ratings are lower (e.g., 1, 2, 3) but also acknowledge strengths.
    It is crucial that you include a concise summary at the end of the bullet points.
    The total output (bullet points and summary combined) should be between 100 and 130 words.
    Format the recommendations strictly as a bulleted list using hyphens.
    Start the summary with "Summary:".
    """

  
    headers = {
        'Content-Type': 'application/json',
    }
    
    params = {
        'key': GEMINI_API_KEY 
    }
   
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ]
    }

    try:
        
        response = requests.post(
            f"{GEMINI_API_URL}",
            headers=headers,
            params=params,
            data=json.dumps(payload) 
        )
        response.raise_for_status() 
        result = response.json() 

        recommendations = []
        summary = ""

        
        if result and result.get("candidates") and len(result["candidates"]) > 0:
            generated_text = result["candidates"][0]["content"]["parts"][0]["text"]

            
            lines = generated_text.split('\n')
            summary_found = False
            for line in lines:
                stripped_line = line.strip()
                if stripped_line.startswith("Summary:"):
                    summary = stripped_line[len("Summary:"):].strip()
                    summary_found = True
                elif stripped_line.startswith('-') and not summary_found:
                   
                    clean_rec = stripped_line.replace('**', '')
                    recommendations.append(clean_rec)
                elif not summary_found and stripped_line: 
                    clean_rec = stripped_line.replace('**', '')
                    recommendations.append(clean_rec)

            
            if not recommendations and not summary:
                
                clean_text = generated_text.strip().replace('**', '')
                recommendations = [clean_text]
                summary = "No distinct summary provided by AI."

            return recommendations, summary
        else:
            return ["Error: No recommendations could be generated by the AI. The response structure was unexpected."], ""
    except requests.exceptions.RequestException as e:
        
        return [f"Error connecting to AI service: {e}. Please check your API key and network connection."], ""
    except json.JSONDecodeError:
        
        return ["Error: Could not parse AI response. The response was not valid JSON."], ""
    except Exception as e:
        
        return [f"An unexpected error occurred: {e}"], ""


st.set_page_config(
    page_title="Employee Wellness & Retention",
    layout="centered", 
    initial_sidebar_state="auto" 
)

st.title("Employee Wellness and Retention Project")
st.markdown("""
This tool helps assess employee wellness and provides AI-driven recommendations for retention.
Please select your department and rate the statements from 1 (Strongly Disagree) to 5 (Strongly Agree).
""")
st.markdown("---")


departments = ["Please Select", "Sales", "Marketing", "Engineering", "Human Resources", "Finance"]
selected_department = st.selectbox(
    "Select your department:",
    departments,
    key="department_select" 
)


if 'ratings' not in st.session_state:
    st.session_state.ratings = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'last_submitted_department' not in st.session_state:
    st.session_state.last_submitted_department = None
if 'last_submitted_ratings' not in st.session_state:
    st.session_state.last_submitted_ratings = {}
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'active_department' not in st.session_state: 
    st.session_state.active_department = "Please Select"


if selected_department != st.session_state.active_department:
    st.session_state.active_department = selected_department
    st.session_state.current_question_index = 0
    st.session_state.ratings = {} 
    st.session_state.submitted = False
    st.session_state.recommendations = [] 
    st.session_state.summary = "" 
    if selected_department != "Please Select": 
        st.rerun()


if selected_department and selected_department != "Please Select":

    st.markdown(f"<h3 style='font-size: 1.1em; margin-top: 1.5em;'>Please rate the following statements on a scale of 1 (Strongly Disagree) to 5 (Strongly Agree) for the {selected_department} department:</h3>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True) 

    department_questions = questions[selected_department]
    total_questions = len(department_questions)

    
    if not st.session_state.submitted:
        
        if st.session_state.current_question_index >= total_questions:
            st.session_state.current_question_index = total_questions - 1 
            st.session_state.submitted = False 

       
        current_question = department_questions[st.session_state.current_question_index]
        
      
        st.markdown(f"<p style='font-size: 1.15em; font-weight: bold;'>{st.session_state.current_question_index + 1}. {current_question}</p>", unsafe_allow_html=True)
        
        
        current_rating_value = st.session_state.ratings.get(current_question, 3)

        
        rating = st.slider(
            " ", 
            1, 5, 
            value=current_rating_value, 
            key=f"{selected_department}_q_{st.session_state.current_question_index}" # Unique key for this specific slider instance
        )
       
        st.session_state.ratings[current_question] = rating

        
        
        
        if st.session_state.current_question_index < total_questions - 1:
            
            col_prev, col_spacer, col_next = st.columns([1, 2, 1]) # Adjusted spacing
            with col_prev:
                if st.session_state.current_question_index > 0:
                    if st.button("Previous", key="prev_button", use_container_width=True):
                        st.session_state.current_question_index -= 1
                        st.rerun()
            with col_next: 
                if st.button("Next", key="next_button", use_container_width=True):
                    st.session_state.current_question_index += 1
                    st.rerun()
        else: 
            
            col_left_spacer, col_submit, col_right_spacer = st.columns([1, 1.5, 1]) # Adjusted ratio for centering
            with col_submit:
                if st.button("Submit Ratings", key="submit_button_final", use_container_width=True):
                    
                    st.session_state.submitted = True
                    
                    st.session_state.last_submitted_department = selected_department
                    st.session_state.last_submitted_ratings = st.session_state.ratings.copy() # Make a copy
                    
                    st.session_state.recommendations = []
                    st.session_state.summary = ""
                    st.rerun() 

elif selected_department == "Please Select":
    st.info("Please select your department to proceed.")


if st.session_state.submitted and st.session_state.last_submitted_department:
    st.subheader("Thank you for your feedback!")
    st.markdown("---")

    
    if not st.session_state.recommendations and not st.session_state.summary:
        st.info("Please wait while AI generates personalized recommendations based on your input.")
        
        with st.spinner('Generating personalized recommendations...'):
            
            recs, summ = get_gemini_recommendations(
                st.session_state.last_submitted_department,
                st.session_state.last_submitted_ratings
            )
            st.session_state.recommendations = recs
            st.session_state.summary = summ
            st.rerun() 

    if st.session_state.recommendations or st.session_state.summary:
        st.subheader("Recommendations for Employee Retention:")
        if st.session_state.recommendations:
            
            for rec in st.session_state.recommendations:
                st.markdown(f"<p style='font-size: 1.1em;'>{rec}</p>", unsafe_allow_html=True)
        else:
            st.warning("No specific recommendations could be generated at this time.")

        if st.session_state.summary:
            st.subheader("Summary:")
            
            st.markdown(f"<p style='font-size: 1.1em;'>{st.session_state.summary}</p>", unsafe_allow_html=True)
        else:
            st.info("No distinct summary was provided by the AI.")

    st.markdown("---")
    st.success("Your feedback is invaluable for improving employee wellness and retention!")
