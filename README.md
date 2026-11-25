AI-Powered Candidate Assessment Platform

An AI-powered candidate assessment platform that automates the process of generating technical assessments from candidate resumes. The system uses Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs) to analyse resume content and generate relevant multiple-choice questions, helping organisations streamline their initial candidate evaluation process.


Key Features

1. User Authentication

User registration and login.

JWT-based authentication.

Protected API endpoints.

Role-based access for administrative operations.

2. Resume Upload and Processing

Upload candidate resumes in PDF and DOCX formats.

Extract relevant textual information from resumes.

Divide extracted content into smaller chunks.

Generate vector embeddings for semantic retrieval.

3. Retrieval-Augmented Generation (RAG)

Uses Sentence Transformers to generate text embeddings.

Uses FAISS for efficient vector similarity search.

Retrieves relevant resume information based on assessment-generation queries.

Provides contextual information to the LLM to generate personalised questions.

4. AI-Powered Assessment Generation

Uses the Groq API to access an LLM.

Automatically generates assessment names and descriptions.

Generates multiple-choice questions based on resume information.

Generates answer choices and identifies the correct answer.

Stores generated assessments and questions in the database.

5. Candidate Assessment

Candidates can view available assessments.

Candidates can attempt multiple-choice questions.

Responses are submitted through the backend API.

The system automatically evaluates submitted answers.

Candidate scores are calculated and stored.

6. Admin Dashboard

Retrieve candidate assessment results.

View individual candidate performance.

View assessment-wise scores.

Inspect submitted answers and question-level results.


Installation and Setup

Prerequisites

Make sure the following are installed:

Python 3.10 or later

Git

A Groq API key

pip

1. Clone the Repository

git clone https://github.com/YOUR_USERNAME/AI-Candidate-Assessment.git

Navigate into the project directory:

cd AI-Candidate-Assessment

2. Create a Virtual Environment

python -m venv venv

Activate the environment.

Windows (PowerShell):

.\venv\Scripts\Activate.ps1

Linux / macOS:

source venv/bin/activate

3. Install Backend Dependencies

pip install -r requirements.txt

4. Install Frontend Dependencies

pip install -r frontend/requirements.txt

5. Configure Environment Variables

Create a .env file in the project root.

GROQ_API_KEY=your_groq_api_key

Replace the placeholder with your actual Groq API key.

Important: Never commit your .env file or expose your API key publicly.

6. Apply Database Migrations

python manage.py makemigrations
python manage.py migrate

7. Create a Superuser

python manage.py createsuperuser

Follow the instructions to create an administrator account.

Running the Application

The backend and frontend run independently and communicate through REST APIs.

1. Start the Django Backend

Open a terminal in the project root:

python manage.py runserver

The backend will be available at:

http://127.0.0.1:8000/

2. Start the Streamlit Frontend

Open another terminal, activate the same virtual environment, and execute:

streamlit run frontend/app.py

The frontend will normally be available at:

http://localhost:8501/
