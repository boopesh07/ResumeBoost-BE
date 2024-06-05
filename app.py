from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
from openai import OpenAI
from models import db, ResumeBoostStatistic, CoverLetterStatistic
from flask_migrate import Migrate
import logging
import os
import json
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# Set up Flask-CORS
CORS(app)

# Set up database URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up secret key for auth
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Auth setup
# Set up Flask-Dance
blueprint = make_google_blueprint(
    client_id="YOUR_GOOGLE_CLIENT_ID",
    client_secret="YOUR_GOOGLE_CLIENT_SECRET",
    scope=["profile", "email"],
    redirect_url="/login/google"
)
app.register_blueprint(blueprint, url_prefix="/login")

# System Prompts
resume_tailor_system_prompt = (
    "You are an expert in rewriting resumes tailored to job descriptions to clear ATS scans and impress technical recruiters. \n\n"
    "1. Examine the job description to identify required skills, qualifications, experience, and keywords.\n"
    "2. Assign an initial score to the resume.\n"
    "3. Rewrite the resume to align with the job description, including necessary keywords to clear the ATS. \n"
    "4. Improve project descriptions using better keywords and sentences without introducing new projects.\n"
    "5. Suggest technical projects that align with the job description.\n\n"
    "Output the results in the following JSON format:\n"
    "{\n"
    "  'tailored_resume': '<tailored resume contents >',\n"
    "  'keywords_inserted': ['<keyword1>', '<keyword2>', ...],\n"
    "  'score_improvement': '<Initial score : 60%, Final score : 90%>',\n"
    "  'project_suggestions': ['<project suggestion 1>', '<project suggestion 2>', ...]\n"
    "}"
)

cover_letter_system_prompt = (
    "You are an expert in writing and tailoring cover letters.\n\n"
    "1. Examine the job description to identify required skills, qualifications, and experience.\n"
    "2. Highlight the candidate's relevant skills, experiences, and enthusiasm for the role.\n"
    "3. Ensure the cover letter is professional, concise, and tailored to the job description.\n\n"
    "Generate the cover letter in a professional tone, focusing on how the candidate’s skills and experiences match the job requirements."
)

def interact_with_GPT(system_prompt, user_message, model="gpt-4o", max_tokens=1500, json_output=False):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    if json_output:
        response = client.chat.completions.create(model=model,
                                                  response_format={"type": "json_object"},
                                                  messages=messages,
                                                  max_tokens=max_tokens)
    else:
        response = client.chat.completions.create(model=model,
                                                  messages=messages,
                                                  max_tokens=max_tokens)
    return response.choices[0].message.content.strip()

@app.route('/generate_resume', methods=['POST'])
def generate_resume():
    data = request.json
    resume_text = data.get('resume_text')
    job_description = data.get('job_description')

    user_message = (
        f"Here is a job description:\n\n\"\"\"\n{job_description}\n\"\"\"\n\n"
        f"And here is a candidate's resume:\n\n\"\"\"\n{resume_text}\n\"\"\"\n\n"
    )

    tailored_resume_results = interact_with_GPT(resume_tailor_system_prompt, user_message, max_tokens=1500, json_output=True)
    # Parse the response JSON
    try:
        response_json = json.loads(tailored_resume_results)
        tailored_resume = response_json.get('tailored_resume')
        keywords_inserted = response_json.get('keywords_inserted')
        score_improvement = response_json.get('score_improvement')
        project_suggestions = response_json.get('project_suggestions')

        # Save to database
        run_id = str(uuid.uuid4())
        resume_boost_entry = ResumeBoostStatistic(
            id=run_id,
            input_resume=resume_text,
            input_job_description=job_description,
            tailored_resume=tailored_resume,
            keywords_inserted=json.dumps(keywords_inserted),  # Save as JSON list
            score_improvement=score_improvement,
            project_suggestions=json.dumps(project_suggestions)
        )
        db.session.add(resume_boost_entry)
        db.session.commit()
        logger.info(f"Saved run ID {run_id} to the database")

    except json.JSONDecodeError as e:
        logger.error(f"JSONDecodeError: {str(e)}")
        return jsonify({'error': 'Failed to parse response from the model'}), 500
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

    return jsonify({'run_id': run_id})

@app.route('/view_resume/<runId>', methods=['GET'])
def view_resume(runId):
    try:
        resume_boost_entry = ResumeBoostStatistic.query.get(runId)
        if resume_boost_entry is None:
            return jsonify({'error': 'Run ID not found'}), 404

        return jsonify({
            'tailored_resume': resume_boost_entry.tailored_resume,
            'keywords_inserted': json.loads(resume_boost_entry.keywords_inserted),
            'score_improvement': resume_boost_entry.score_improvement,
            'project_suggestions': json.loads(resume_boost_entry.project_suggestions)
        })
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/generate_cover_letter', methods=['POST'])
def generate_cover_letter():
    data = request.json
    resume_text = data.get('resume_text')
    job_description = data.get('job_description')

    user_message = (
        f"Here is a job description:\n\n\"\"\"\n{job_description}\n\"\"\"\n\n"
        f"And here is a candidate's resume:\n\n\"\"\"\n{resume_text}\n\"\"\"\n\n"
        "Ensure the cover letter is professional and concise, without placeholders, using information from both the resume and job description."
    )

    try:
        cover_letter = interact_with_GPT(cover_letter_system_prompt, user_message, max_tokens=1000)

        # Save to database
        run_id = str(uuid.uuid4())
        cover_letter_entry = CoverLetterStatistic(
            id=run_id,
            input_resume=resume_text,
            input_job_description=job_description,
            cover_letter=cover_letter
        )
        db.session.add(cover_letter_entry)
        db.session.commit()
        logger.info(f"Saved run ID {run_id} to the database")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

    return jsonify({'run_id': run_id})

@app.route('/view_cover/<runId>', methods=['GET'])
def view_cover(runId):
    try:
        cover_letter_entry = CoverLetterStatistic.query.get(runId)
        if cover_letter_entry is None:
            return jsonify({'error': 'Run ID not found'}), 404

        return jsonify({
            'cover_letter': cover_letter_entry.cover_letter
        })
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/login/google')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        user_info = resp.json()
        email = user_info["email"]
        return "You are {email} on Google.".format(email=email)  # You will need to pass this information back to the frontend
    return "Failed to fetch user info."

if __name__ == '__main__':
    app.run(debug=True)
