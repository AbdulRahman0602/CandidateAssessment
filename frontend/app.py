
import streamlit as st
import requests
import pandas as pd


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Candidate Assessment",
    page_icon="🎓",
    layout="wide"
)


# =========================================================
# API CONFIGURATION
# =========================================================

BASE_URL = "http://127.0.0.1:8000"

# Authentication APIs
LOGIN_API = "/api/v1/token/"
SIGNUP_API = "/api/v1/user/signup/"

UPLOAD_RESUME_API = "/api/v1/assessments/file/upload/"

CREATE_ASSESSMENT_API = "/api/v1/assessments/assessment/create/"

GET_ASSESSMENTS_API = "/api/v1/assessments/assessment/list/"

SAVE_RESPONSES_API = "/api/v1/assessments/assessment/save_response/"

ADMIN_MARKS_API = "/api/v1/assessments/admin/candidate-marks/"


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "token": None,
    "refresh_token": None,
    "email": None,
    "authenticated": False,
    "assessments": [],
    "candidate_results": [],
    "assessment_result": None,
    "submitted_assessments": []
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# API HELPER FUNCTIONS
# =========================================================

def get_headers():

    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


def api_get(endpoint):

    try:

        response = requests.get(
            BASE_URL + endpoint,
            headers=get_headers(),
            timeout=60
        )

        return response

    except requests.RequestException as e:

        st.error(f"Connection error: {e}")
        return None


def api_post(endpoint, data=None, files=None):

    try:

        response = requests.post(
            BASE_URL + endpoint,
            headers=get_headers(),
            json=data if files is None else None,
            files=files,
            timeout=180
        )

        return response

    except requests.RequestException as e:

        st.error(f"Connection error: {e}")
        return None


def show_api_error(response):

    try:
        st.error(response.json())

    except ValueError:
        st.error(response.text)


# =========================================================
# AUTHENTICATION FUNCTIONS
# =========================================================

def signup(email, password):

    payload = {
        "email": email,
        "password": password
    }

    try:

        response = requests.post(
            BASE_URL + SIGNUP_API,
            json=payload,
            timeout=30
        )

        return response

    except requests.RequestException as e:

        st.error(f"Connection error: {e}")
        return None


def login(email, password):

    payload = {
        "email": email,
        "password": password
    }

    try:

        response = requests.post(
            BASE_URL + LOGIN_API,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:

            token_data = response.json()

            access_token = token_data.get("access")

            if not access_token:
                st.error("Access token was not returned.")
                return False

            st.session_state.token = access_token
            st.session_state.refresh_token = token_data.get("refresh")
            st.session_state.email = email
            st.session_state.authenticated = True

            st.session_state.assessments = []
            st.session_state.candidate_results = []
            st.session_state.assessment_result = None
            st.session_state.submitted_assessments = []

            return True

        else:

            show_api_error(response)
            return False

    except requests.RequestException as e:

        st.error(f"Connection error: {e}")
        return False


def logout():

    st.session_state.token = None
    st.session_state.refresh_token = None
    st.session_state.email = None
    st.session_state.authenticated = False

    st.session_state.assessments = []
    st.session_state.candidate_results = []
    st.session_state.assessment_result = None
    st.session_state.submitted_assessments = []

    st.rerun()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🎓 Candidate Assessment")

st.sidebar.caption("AI-powered Resume Assessment Platform")

st.sidebar.divider()

BASE_URL = st.sidebar.text_input(
    "Backend URL",
    value=BASE_URL
).rstrip("/")

if st.session_state.authenticated:

    st.sidebar.success(
        f"Logged in as {st.session_state.email}"
    )

    if st.sidebar.button("Logout", use_container_width=True):
        logout()

    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigation",
        [
            "Home",
            "Upload Resume",
            "Generate Assessment",
            "Take Assessment",
            "Admin Dashboard"
        ]
    )

else:

    page = st.sidebar.radio(
        "Navigation",
        [
            "Sign In",
            "Sign Up"
        ]
    )


# =========================================================
# SIGN UP PAGE
# =========================================================

if not st.session_state.authenticated and page == "Sign Up":

    st.title("📝 Create Your Account")

    st.write(
        "Register to access the AI Candidate Assessment Platform."
    )

    with st.form("signup_form"):

        email = st.text_input(
            "Email Address"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Create Account",
            type="primary",
            use_container_width=True
        )

        if submitted:

            if not email or not password:

                st.warning("Please enter your email and password.")

            elif password != confirm_password:

                st.error("Passwords do not match.")

            else:

                with st.spinner("Creating your account..."):

                    response = signup(email, password)

                if response is not None:

                    if response.status_code in [200, 201]:

                        st.success(
                            "Account created successfully! "
                            "You can now sign in."
                        )

                    else:

                        st.error("Registration failed.")
                        show_api_error(response)


# =========================================================
# SIGN IN PAGE
# =========================================================

elif not st.session_state.authenticated and page == "Sign In":

    st.title("🔐 Welcome Back")

    st.write(
        "Sign in to access your assessment dashboard."
    )

    with st.form("signin_form"):

        email = st.text_input(
            "Email Address"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Sign In",
            type="primary",
            use_container_width=True
        )

        if submitted:

            if not email or not password:

                st.warning("Please enter your email and password.")

            else:

                with st.spinner("Signing in..."):

                    success = login(email, password)

                if success:

                    st.success("Login successful!")

                    st.rerun()


# =========================================================
# HOME PAGE
# =========================================================

elif st.session_state.authenticated and page == "Home":

    st.title("🎓 AI Candidate Assessment Platform")

    st.write(
        "Generate technical assessments automatically "
        "from candidate resumes using RAG and Groq."
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("👨‍💻 Candidate")

        st.markdown(
            """
            - Upload your resume.
            - Generate an AI-based assessment.
            - Answer multiple-choice questions.
            - Submit your responses.
            - View your submission score.
            """
        )

    with col2:

        st.subheader("🛠️ Administrator")

        st.markdown(
            """
            - View candidate assessment results.
            - Check total marks obtained.
            - Review individual candidate responses.
            """
        )

    st.divider()

    st.info(
        "Choose an option from the sidebar to get started."
    )


# =========================================================
# RESUME UPLOAD PAGE
# =========================================================

elif st.session_state.authenticated and page == "Upload Resume":

    st.title("📄 Upload Resume")

    st.write(
        "Upload your PDF or DOCX resume."
    )

    uploaded_file = st.file_uploader(
        "Choose your resume",
        type=["pdf", "docx"]
    )

    if st.button(
        "Upload Resume",
        type="primary",
        disabled=uploaded_file is None
    ):

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type
            )
        }

        with st.spinner("Uploading resume..."):

            response = api_post(
                UPLOAD_RESUME_API,
                files=files
            )

        if response is not None:

            if response.status_code in [200, 201]:

                st.success("Resume uploaded successfully!")

                st.json(response.json())

            else:

                st.error("Resume upload failed.")
                show_api_error(response)


# =========================================================
# GENERATE ASSESSMENT PAGE
# =========================================================

elif st.session_state.authenticated and page == "Generate Assessment":

    st.title("🤖 Generate Assessment")

    st.write(
        "Generate an assessment automatically from your latest uploaded resume."
    )

    st.info(
        """
        Your backend uses:

        - FAISS for retrieving relevant resume content.
        - Sentence Transformers for embeddings.
        - Groq LLM for generating the assessment.
        """
    )

    if st.button(
        "Generate Assessment",
        type="primary"
    ):

        with st.spinner(
            "Generating assessment using Groq. Please wait..."
        ):

            response = api_post(
                CREATE_ASSESSMENT_API,
                data={}
            )

        if response is not None:

            if response.status_code in [200, 201]:

                result = response.json()

                st.success(
                    "Assessment generated successfully!"
                )

                st.json(result)

                st.session_state.assessments = []

            else:

                st.error("Assessment generation failed.")
                show_api_error(response)


# =========================================================
# TAKE ASSESSMENT PAGE
# =========================================================

elif st.session_state.authenticated and page == "Take Assessment":

    st.title("📝 Take Assessment")

    if st.button("Load Assessments"):

        with st.spinner("Retrieving assessments..."):

            response = api_get(GET_ASSESSMENTS_API)

        if response is not None:

            if response.status_code == 200:

                result = response.json()

                st.session_state.assessments = result.get(
                    "data", []
                )

                st.success("Assessments retrieved successfully!")

            else:

                st.error("Unable to retrieve assessments.")
                show_api_error(response)

    assessments = st.session_state.assessments

    if assessments:

        assessment_options = {
            f"{item['name']} (ID: {item['id']})": item
            for item in assessments
        }

        selected_name = st.selectbox(
            "Select an assessment",
            list(assessment_options.keys())
        )

        assessment = assessment_options[selected_name]

        st.divider()

        st.subheader(assessment["name"])

        st.write(
            assessment.get("description", "")
        )

        questions = assessment.get("questions", [])

        st.write(f"Total Questions: {len(questions)}")

        if not questions:

            st.warning("This assessment has no questions.")

        else:

            answers = {}

            st.divider()

            for index, question in enumerate(questions):

                question_id = question["id"]

                st.markdown(
                    f"### Question {question.get('qn_no', index + 1)}"
                )

                st.write(question["text"])

                choices = question.get("choices", [])

                if not choices:

                    st.warning(
                        "No choices available for this question."
                    )

                    continue

                selected_choice = st.radio(
                    "Select your answer:",
                    options=choices,
                    format_func=lambda choice: choice["text"],
                    key=f"assessment_{assessment['id']}_question_{question_id}",
                    index=None
                )

                if selected_choice is not None:

                    answers[question_id] = selected_choice["id"]

                st.divider()

            assessment_id = assessment["id"]

            if assessment_id in st.session_state.submitted_assessments:

                st.info(
                    "You have already submitted this assessment in this session."
                )

            elif st.button(
                "Submit Assessment",
                type="primary"
            ):

                if len(answers) != len(questions):

                    st.warning(
                        "Please answer all questions before submitting."
                    )

                else:

                    payload = {
                        "assessment_id": assessment_id,
                        "responses": [
                            {
                                "question_id": question_id,
                                "selected_choice_id": choice_id
                            }
                            for question_id, choice_id in answers.items()
                        ]
                    }

                    with st.spinner("Submitting your responses..."):

                        response = api_post(
                            SAVE_RESPONSES_API,
                            data=payload
                        )

                    if response is not None:

                        if response.status_code in [200, 201]:

                            result = response.json()

                            st.session_state.assessment_result = result

                            st.session_state.submitted_assessments.append(
                                assessment_id
                            )

                            st.success(
                                "Assessment submitted successfully!"
                            )

                            st.subheader("Your Result")

                            col1, col2 = st.columns(2)

                            with col1:

                                st.metric(
                                    "Marks Obtained",
                                    result.get("score", 0)
                                )

                            with col2:

                                st.metric(
                                    "Total Questions",
                                    result.get("total_questions", 0)
                                )

                        else:

                            st.error("Submission failed.")
                            show_api_error(response)

    else:

        st.info(
            "Click 'Load Assessments' to retrieve your assessments."
        )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

elif st.session_state.authenticated and page == "Admin Dashboard":

    st.title("📊 Admin Dashboard")

    st.write(
        "View candidate marks and assessment performance."
    )

    if st.button(
        "Load Candidate Results",
        type="primary"
    ):

        with st.spinner("Retrieving candidate results..."):

            response = api_get(ADMIN_MARKS_API)

        if response is not None:

            if response.status_code == 200:

                result = response.json()

                st.session_state.candidate_results = result.get(
                    "data", []
                )

                st.success(
                    "Candidate results retrieved successfully!"
                )

            elif response.status_code == 403:

                st.error(
                    "Access denied. Only Django staff users can access this page."
                )

            else:

                st.error("Unable to retrieve candidate results.")
                show_api_error(response)

    candidate_data = st.session_state.candidate_results

    if candidate_data:

        st.divider()

        st.subheader("Overall Candidate Results")

        table_data = []

        for item in candidate_data:

            table_data.append({

                "Candidate": item.get("candidate"),

                "Candidate ID": item.get("candidate_id"),

                "Assessment": item.get("assessment_name"),

                "Assessment ID": item.get("assessment_id"),

                "Total Questions": item.get("total_questions"),

                "Marks Obtained": item.get("total_marks")

            })

        df = pd.DataFrame(table_data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("Individual Candidate Details")

        candidate_options = {}

        for index, item in enumerate(candidate_data):

            label = (
                f"{item.get('candidate')} - "
                f"{item.get('assessment_name')} "
                f"(Assessment ID: {item.get('assessment_id')})"
            )

            candidate_options[f"{label} - {index}"] = item

        selected_candidate = st.selectbox(
            "Select candidate",
            list(candidate_options.keys())
        )

        selected_data = candidate_options[selected_candidate]

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Candidate",
                selected_data.get("candidate", "N/A")
            )

        with col2:

            st.metric(
                "Total Questions",
                selected_data.get("total_questions", 0)
            )

        with col3:

            st.metric(
                "Marks Obtained",
                selected_data.get("total_marks", 0)
            )

        st.write(
            "**Assessment:**",
            selected_data.get("assessment_name")
        )

        st.divider()

        st.subheader("Question-wise Results")

        for index, item in enumerate(
            selected_data.get("responses", [])
        ):

            st.markdown(
                f"**Question {index + 1}:** {item.get('question')}"
            )

            selected_choices = item.get(
                "selected_choices", []
            )

            st.write(
                "Selected Answer:",
                ", ".join(selected_choices)
            )

            if item.get("score", 0) == 1:

                st.success("Correct Answer — 1 mark")

            else:

                st.error("Incorrect Answer — 0 marks")

            st.divider()

    elif candidate_data == []:

        st.info(
            "No candidate results available. Click 'Load Candidate Results' to refresh."
        )


# =========================================================
# FOOTER
# =========================================================

st.sidebar.divider()

st.sidebar.caption(
    "AI Candidate Assessment Platform"
)
