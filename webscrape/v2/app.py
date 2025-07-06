# app.py

from flask import Flask, render_template, request, Response
import json
import threading
import queue
from scraper_api import scrape_jobs_stream

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    # Required
    keywords = request.args.get('keywords', '').strip()
    location = request.args.get('location', '').strip()
    if not keywords or not location:
        return Response("keywords and location are required", status=400)

    # Optional
    time_filter = request.args.get('time_filter', '')
    job_type    = request.args.get('job_type', '')
    work_type   = request.args.get('work_type', '')
    experience  = request.args.get('experience', '')
    max_results = int(request.args.get('max_results', 60))

    # Prepare the output file (overwrite)
    jobs_file = 'jobs.json'
    with open(jobs_file, 'w') as f:
        json.dump([], f)

    # Thread-safe queue for streaming jobs
    q = queue.Queue()

    # Background worker: scrape and enqueue
    def worker():
        for job in scrape_jobs_stream(
            keywords, location, time_filter, job_type,
            max_results=max_results, work_type=work_type, experience=experience
        ):
            # Append to JSON file
            # Load-modify-write (could be optimized with incremental writes)
            with open(jobs_file, 'r+') as f:
                data = json.load(f)
                data.append(job)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
            # Push to queue for streaming
            q.put(job)
        # Signal completion
        q.put(None)

    threading.Thread(target=worker, daemon=True).start()

    # SSE event-stream: consume queue
    def event_stream():
        while True:
            job = q.get()
            if job is None:
                break
            yield f"data: {json.dumps(job)}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)
