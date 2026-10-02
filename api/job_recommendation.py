from flask import Blueprint, current_app, jsonify, request
import requests

bp = Blueprint("job_rec", __name__)

@bp.route("/recommend", methods=["POST"])
def llm_recommend_jobs():
    """
    POST /recommend
    Body JSON: { "user_id": int }
    Returns JSON: { "recommendations": [string] }
    """
    data = request.get_json() or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    # Fetch user resumes
    base = current_app.config.get('INTERNAL_API_BASE', 'http://localhost:7860')
    resumes_url = f"{base}/api/users/{user_id}/resumes"
    try:
        resp = requests.get(resumes_url, timeout=5)
        resp.raise_for_status()
        resumes = resp.json()
    except Exception as e:
        current_app.logger.error(f"Error fetching resumes for {user_id}: {e}")
        return jsonify({"error": "Failed to fetch user resumes"}), 502

    # Build user profile
    if not resumes:
        profile = {'skills': [], 'experience': '', 'education': '', 'certifications': [], 'preferred_domains': []}
    else:
        r0 = resumes[0]
        profile = {
            'skills': [s.get('name') for s in r0.get('skills', []) if s.get('name')],
            'experience': '; '.join(e.get('position') for e in r0.get('experience', []) if e.get('position')),
            'education': '; '.join(ed.get('degree') for ed in r0.get('education', []) if ed.get('degree')),
            'certifications': [c.get('name') for c in r0.get('certifications', []) if c.get('name')],
            'preferred_domains': r0.get('preferred_domains', []) or []
        }

    # Construct prompt content
    prompt_content = (
        "You are a career recommendation assistant. Suggest 5-7 suitable job titles based on the user profile."
        f"\nSkills: {', '.join(profile['skills']) or 'None'}"
        f"\nExperience: {profile['experience'] or 'None'}"
        f"\nEducation: {profile['education'] or 'None'}"
        f"\nCertifications: {', '.join(profile['certifications']) or 'None'}"
        f"\nPreferred Domains: {', '.join(profile['preferred_domains']) or 'None'}"
        "\nReturn a JSON array of job titles, from most to least relevant."
    )

    # NVIDIA LLM API settings
    invoke_url = current_app.config.get('NVIDIA_API_URL', 'https://integrate.api.nvidia.com/v1/chat/completions')
    api_key = current_app.config.get('NVIDIA_API_KEY')
    if not api_key:
        return jsonify({"error": "Missing NVIDIA_API_KEY in config"}), 500

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    payload = {
        "model": current_app.config.get('NVIDIA_MODEL', 'meta/llama-3.2-11b-vision-instruct'),
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt_content}
        ],
        "max_tokens": current_app.config.get('NVIDIA_MAX_TOKENS', 512),
        "temperature": current_app.config.get('NVIDIA_TEMPERATURE', 0.2),
        "top_p": current_app.config.get('NVIDIA_TOP_P', 0.7),
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "stream": False
    }

    # Call NVIDIA API
    try:
        response = requests.post(invoke_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        current_app.logger.error(f"NVIDIA API call failed: {e}")
        return jsonify({"error": "LLM API call failed"}), 502

    # Extract content robustly
    import json
    import re
    try:
        content = result['choices'][0]['message']['content']
        # Try to find a JSON array in the text
        match = re.search(r'\[\s*\{.*?\}\s*\]|\[\s*".*?"\s*\]', content, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            json_str = content
            
        jobs_data = json.loads(json_str)
        
        jobs = []
        for item in jobs_data:
            if isinstance(item, dict) and "jobTitle" in item:
                jobs.append(item["jobTitle"])
            elif isinstance(item, dict) and "title" in item:
                jobs.append(item["title"])
            elif isinstance(item, str):
                jobs.append(item)
    except Exception as e:
        current_app.logger.error(f"JSON parsing failed, falling back to string extraction: {e}")
        # Fallback string manipulation
        content = result['choices'][0]['message']['content']
        jobs = []
        for line in content.split('\n'):
            line = line.strip().strip('-*0123456789. ')
            # If line is a valid job title and not part of json schema
            if line and "{" not in line and "}" not in line and "json" not in line.lower() and len(line) < 50:
                jobs.append(line.replace('"', '').replace("'", ""))
                
    # Force exactly 5 jobs
    jobs = jobs[:5]
    if not jobs:
        jobs = ["Software Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer", "Data Analyst"]

    return jsonify({"recommendations": jobs}), 200

# Note: Configure NVIDIA_API_KEY, NVIDIA_API_URL, NVIDIA_MODEL in Flask config.

import os
from flask import send_file, request, jsonify
import logging
import requests

logger = logging.getLogger(__name__)

API_RECOMMEND_URL = "http://localhost:7860/api/recommend"
HEADERS = {"Content-Type": "application/json"}

@bp.route("/recommended_jobs", methods=["GET"])
def get_recommended_jobs():
    """
    GET /recommended_jobs
    Returns the JSON content of recommended_jobs.json file
    """
    import tempfile
    json_path = os.path.join(tempfile.gettempdir(), 'recommended_jobs.json')
    if not os.path.exists(json_path):
        return jsonify({"error": "recommended_jobs.json file not found"}), 404
    return send_file(json_path, mimetype='application/json')

def extract_job_titles(recommendations_json):
    """
    Extract job titles from recommendations JSON
    """
    titles = []
    if 'recommendations' in recommendations_json:
        for title in recommendations_json['recommendations']:
            if isinstance(title, str):
                cleaned = title.strip().strip('"').strip("'")
                if cleaned:
                    titles.append(cleaned)
    return titles

from utils.linkedin_ws import scrape_linkedin_jobs


def scrape_all_titles(titles, location):
    """
    Scrape jobs for all titles and aggregate results.
    Filters out invalid listings and limits to 12 per title.
    """
    all_jobs = []
    for title in titles:
        jobs = scrape_linkedin_jobs(title, location)
        # Filter out listings with obfuscated fields
        filtered_jobs = [
            job for job in jobs
            if job.get('title') and '*' not in job.get('title') and
               job.get('company') and '*' not in job.get('company') and
               job.get('location') and '*' not in job.get('location')
        ]
        # Limit to 12 listings per title
        limited_jobs = filtered_jobs[:12]
        all_jobs.extend(limited_jobs)
    return all_jobs

def save_jobs(all_jobs):
    """
    Save jobs to recommended_jobs.json file
    """
    import json
    import tempfile
    json_path = os.path.join(tempfile.gettempdir(), 'recommended_jobs.json')
    with open(json_path, 'w') as f:
        json.dump(all_jobs, f, indent=2)

@bp.route('/run-scraper', methods=['POST'])
def run_scraper():
    data = request.get_json() or {}
    titles = data.get('titles')
    location = data.get('location')
    if not titles or not location:
        return jsonify({'error': 'titles and location required'}), 400
    
    # Extract and scrape
    all_jobs = scrape_all_titles(titles, location)
    # Overwrite JSON file
    save_jobs(all_jobs)
    return jsonify({'recommended_jobs': all_jobs}), 200
