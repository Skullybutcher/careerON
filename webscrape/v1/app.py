from flask import Flask, render_template, request, Response
import json
from scraper_api import scrape_jobs_via_api

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    # --- Required fields ---
    keywords = request.args.get('keywords', '').strip()
    location = request.args.get('location', '').strip()
    if not keywords or not location:
        return Response("Missing required fields", status=400)
    
    # --- Optional filters ---
    time_filter = request.args.get('time_filter', '')  # '' means any
    job_type    = request.args.get('job_type', '')
    work_type   = request.args.get('work_type', '')    # codes 1,2,3
    experience  = request.args.get('experience', '')   # codes 1–6
    
    # max results
    maxr = int(request.args.get('max_results', 60))
    
    # --- Call scraper_api with all provided filters ---
    jobs = scrape_jobs_via_api(
        keywords=keywords,
        location=location,
        time_filter=time_filter,
        job_type=job_type,
        max_results=maxr,
        page_size=25,
        # pass through extra params
        work_type=work_type,
        experience=experience
    )
    
    # Save to JSON file
    with open('jobs.json', 'w') as f:
        json.dump(jobs, f, indent=2)
    
    # Stream via SSE
    def event_stream():
        for job in jobs:
            yield f"data: {json.dumps(job)}\n\n"
    
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)
