from flask import Flask, render_template, request, jsonify
from scraper import scrape_jobs

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # Get form data
    keywords = request.form.get('keywords')
    location = request.form.get('location')
    time_filter = request.form.get('time_filter')
    job_type = request.form.get('job_type')

    # Scrape jobs
    jobs = scrape_jobs(keywords, location, time_filter, job_type)
    
    # Return jobs as JSON
    return jsonify(jobs)

if __name__ == "__main__":
    app.run(debug=True)
