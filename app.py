from flask import Flask, request, jsonify
from openai import OpenAI
import os
import json

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

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
    "  'tailored_resume': '<tailored resume>',\n"
    "  'keywords_inserted': ['<keyword1>', '<keyword2>', ...],\n"
    "  'score_improvement': '<score improvement>',\n"
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
        keywords_inserted = '-' + '\n- '.join(keywords_inserted)
        score_improvement = response_json.get('score_improvement')
        project_suggestions = response_json.get('project_suggestions')
        project_suggestions = '-' + '\n- '.join(project_suggestions)
    except json.JSONDecodeError:

        return jsonify({'error': 'Failed to parse response from the model'}), 500

    return jsonify({
        'tailored_resume': tailored_resume,
        'keywords_inserted': keywords_inserted,
        'score_improvement': score_improvement,
        'project_suggestions': project_suggestions
    })

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

    cover_letter = interact_with_GPT(cover_letter_system_prompt, user_message, max_tokens=1000)
    return jsonify({'cover_letter': cover_letter})

if __name__ == '__main__':
    app.run(debug=True)
