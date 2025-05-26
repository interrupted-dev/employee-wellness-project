import streamlit as st
import json
import requests # Used for making HTTP requests to the Gemini API

# --- Configuration for Gemini API ---
# IMPORTANT: In a production environment, never hardcode API keys.
# Use Streamlit secrets (st.secrets) or environment variables.
# For this example, we'll leave it as an empty string. Canvas will automatically
# provide the API key at runtime if it's an empty string.

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# GEMINI_API_KEY = "AIzaSyCoBAZzNOnd2mKMnyNoxZC83KJVpRVCOVI"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# --- Questions Data for Each Department ---
# Each department has a list of questions. Answers are expected as ratings from 1 to 5.
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

# --- Function to get recommendations from Gemini API ---
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
    # Construct the prompt for the Gemini model
    prompt_text = f"""
    An employee from the {department} department has provided feedback on their wellness and satisfaction.
    Their ratings (1=Strongly Disagree, 5=Strongly Agree) are as follows:

    """
    # Add each question and its rating to the prompt
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

    # Define headers for the API request
    headers = {
        'Content-Type': 'application/json',
    }
    # Define parameters, including the API key
    params = {
        'key': GEMINI_API_KEY # Canvas will populate this if GEMINI_API_KEY is an empty string
    }
    # Define the payload for the API request
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
        # Make the POST request to the Gemini API
        response = requests.post(
            f"{GEMINI_API_URL}",
            headers=headers,
            params=params,
            data=json.dumps(payload) # Convert payload to JSON string
        )
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        result = response.json() # Parse the JSON response

        recommendations = []
        summary = ""

        # Extract the generated text from the API response
        if result and result.get("candidates") and len(result["candidates"]) > 0:
            generated_text = result["candidates"][0]["content"]["parts"][0]["text"]

            # Split the generated text into lines
            lines = generated_text.split('\n')
            summary_found = False
            for line in lines:
                stripped_line = line.strip()
                if stripped_line.startswith("Summary:"):
                    summary = stripped_line[len("Summary:"):].strip()
                    summary_found = True
                elif stripped_line.startswith('-') and not summary_found:
                    # Remove any markdown bolding from the recommendation text
                    clean_rec = stripped_line.replace('**', '')
                    recommendations.append(clean_rec)
                elif not summary_found and stripped_line: # Catch any non-bullet, non-summary text before summary
                    clean_rec = stripped_line.replace('**', '')
                    recommendations.append(clean_rec)

            # Fallback if no bullet points or summary were explicitly parsed
            if not recommendations and not summary:
                # If no specific formatting was found, treat the whole response as one recommendation
                clean_text = generated_text.strip().replace('**', '')
                recommendations = [clean_text]
                summary = "No distinct summary provided by AI."

            return recommendations, summary
        else:
            return ["Error: No recommendations could be generated by the AI. The response structure was unexpected."], ""
    except requests.exceptions.RequestException as e:
        # Handle network-related errors (e.g., connection refused, timeout)
        return [f"Error connecting to AI service: {e}. Please check your API key and network connection."], ""
    except json.JSONDecodeError:
        # Handle cases where the API response is not valid JSON
        return ["Error: Could not parse AI response. The response was not valid JSON."], ""
    except Exception as e:
        # Handle any other unexpected errors
        return [f"An unexpected error occurred: {e}"], ""

# --- Streamlit Application Layout ---
# Set basic page configuration for better aesthetics
st.set_page_config(
    page_title="Employee Wellness & Retention",
    layout="centered", # 'centered' or 'wide'
    initial_sidebar_state="auto" # 'auto', 'expanded', or 'collapsed'
)

st.title("Employee Wellness and Retention Project")
st.markdown("""
This tool helps assess employee wellness and provides AI-driven recommendations for retention.
Please select your department and rate the statements from 1 (Strongly Disagree) to 5 (Strongly Agree).
""")
st.markdown("---")

# Department Selection Dropdown
departments = ["Please Select", "Sales", "Marketing", "Engineering", "Human Resources", "Finance"]
selected_department = st.selectbox(
    "Select your department:",
    departments,
    key="department_select" # Unique key for the widget
)

# Initialize session state variables
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
if 'active_department' not in st.session_state: # New state variable to track the currently active department for questions
    st.session_state.active_department = "Please Select"

# Logic to reset state when department changes
if selected_department != st.session_state.active_department:
    st.session_state.active_department = selected_department
    st.session_state.current_question_index = 0
    st.session_state.ratings = {} # Clear ratings for the new department
    st.session_state.submitted = False # Reset submission status
    st.session_state.recommendations = [] # Clear old recommendations
    st.session_state.summary = "" # Clear old summary
    if selected_department != "Please Select": # Only rerun if a real department is selected
        st.rerun()

# Logic for displaying questions one by one
if selected_department and selected_department != "Please Select":
    # Adjusted font size and added top margin for the subheader
    st.markdown(f"<h3 style='font-size: 1.1em; margin-top: 1.5em;'>Please rate the following statements on a scale of 1 (Strongly Disagree) to 5 (Strongly Agree) for the {selected_department} department:</h3>", unsafe_allow_html=True)
    # Add a gap between the subheader and the first question
    st.markdown("<br>", unsafe_allow_html=True) 

    department_questions = questions[selected_department]
    total_questions = len(department_questions)

    # Display the current question if not submitted
    if not st.session_state.submitted:
        # Ensure index is within bounds
        if st.session_state.current_question_index >= total_questions:
            st.session_state.current_question_index = total_questions - 1 # Cap at last question if somehow over
            st.session_state.submitted = False # Reset submission if department changes after completion

        # --- ONLY DISPLAY THE CURRENT QUESTION ---
        current_question = department_questions[st.session_state.current_question_index]
        
        # Use st.markdown for the question text to control font size
        st.markdown(f"<p style='font-size: 1.15em; font-weight: bold;'>{st.session_state.current_question_index + 1}. {current_question}</p>", unsafe_allow_html=True)
        
        # Get the current rating for this question, or default to 3 if not yet rated
        current_rating_value = st.session_state.ratings.get(current_question, 3)

        # Display the slider for the current question
        rating = st.slider(
            " ", # Empty label for the slider itself, as the question is above it
            1, 5, # Min and Max values for the slider
            value=current_rating_value, # Set the initial value of the slider
            key=f"{selected_department}_q_{st.session_state.current_question_index}" # Unique key for this specific slider instance
        )
        # Store the rating for the current question
        st.session_state.ratings[current_question] = rating

        # Navigation Buttons
        # Use columns for better alignment of Previous/Next/Submit buttons
        # Adjusted column ratios to center the submit button and align prev/next
        if st.session_state.current_question_index < total_questions - 1:
            # For Previous and Next buttons
            col_prev, col_spacer, col_next = st.columns([1, 2, 1]) # Adjusted spacing
            with col_prev:
                if st.session_state.current_question_index > 0:
                    if st.button("Previous", key="prev_button", use_container_width=True):
                        st.session_state.current_question_index -= 1
                        st.rerun()
            with col_next: # Place "Next" button in the rightmost column
                if st.button("Next", key="next_button", use_container_width=True):
                    st.session_state.current_question_index += 1
                    st.rerun()
        else: # On the last question, show Submit button, centered
            # Adjusted columns for better centering of the submit button
            col_left_spacer, col_submit, col_right_spacer = st.columns([1, 1.5, 1]) # Adjusted ratio for centering
            with col_submit:
                if st.button("Submit Ratings", key="submit_button_final", use_container_width=True):
                    # st.write("Submit button clicked!") # Debugging line to confirm click - removed for cleaner UI
                    st.session_state.submitted = True
                    # Store the department and ratings that were just submitted
                    st.session_state.last_submitted_department = selected_department
                    st.session_state.last_submitted_ratings = st.session_state.ratings.copy() # Make a copy
                    # Clear previous recommendations and summary to show loading state
                    st.session_state.recommendations = []
                    st.session_state.summary = ""
                    st.rerun() # Trigger a rerun to immediately show the "Generating Recommendations..." message

elif selected_department == "Please Select":
    st.info("Please select your department to proceed.")

# Display Recommendations after submission
if st.session_state.submitted and st.session_state.last_submitted_department:
    st.subheader("Thank you for your feedback!")
    st.markdown("---")

    # Only call API if recommendations haven't been generated yet for the current submission
    if not st.session_state.recommendations and not st.session_state.summary:
        st.info("Please wait while AI generates personalized recommendations based on your input.")
        # Use a spinner to indicate that recommendations are being generated
        with st.spinner('Generating personalized recommendations...'):
            # Call the Gemini API function using the stored submitted data
            recs, summ = get_gemini_recommendations(
                st.session_state.last_submitted_department,
                st.session_state.last_submitted_ratings
            )
            st.session_state.recommendations = recs
            st.session_state.summary = summ
            st.rerun() # Rerun to display the generated content

    if st.session_state.recommendations or st.session_state.summary:
        st.subheader("Recommendations for Employee Retention:")
        if st.session_state.recommendations:
            # Display each recommendation as a markdown bullet point with increased font size
            for rec in st.session_state.recommendations:
                st.markdown(f"<p style='font-size: 1.1em;'>{rec}</p>", unsafe_allow_html=True)
        else:
            st.warning("No specific recommendations could be generated at this time.")

        if st.session_state.summary:
            st.subheader("Summary:")
            # Display summary with increased font size
            st.markdown(f"<p style='font-size: 1.1em;'>{st.session_state.summary}</p>", unsafe_allow_html=True)
        else:
            st.info("No distinct summary was provided by the AI.")

    st.markdown("---")
    st.success("Your feedback is invaluable for improving employee wellness and retention!")
