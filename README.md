# ResumeBoost-BE

ResumeBoost-BE is the backend code for the ResumeBoost platform. It helps users tailor their resumes according to job descriptions and generate personalized cover letters. This backend engine supports both the Chrome extension and web applications.

## Features

- Tailor resumes to match specific job descriptions
- Generate personalized cover letters
- Supports both web and Chrome extension integrations

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Virtual environment tool (e.g., `venv` or `virtualenv`)

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/ResumeBoost-BE.git
cd ResumeBoost-BE
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv .virtualEnv
source .virtualEnv/bin/activate
```

### 3. Install the Required Packages

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a .env file in the root directory of the project and add your OpenAI API key in the below format:

OPENAI_API_KEY=your_openai_api_key

### 5. Run the Backend application
You can choose to run the Flask application directly from your IDE like PyCharm or also prefer the below approach of running from CLI
```bash
python app.py
```

### 6. Run the Streamlit Application
Once the backend application is running successfully, you can run the Streamlit application to start using the MVP of the platform. 
```bash
streamlit run streamlit_app.py
```

