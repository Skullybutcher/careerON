from flask import Flask, render_template, request, Response
import json
import threading
import queue
from scraper_api import scrape_jobs_stream  # Make sure this function yields one job at a time

app = Flask(__name__)
file_lock = threading.Lock()  # 🔒 Lock for safe JSON read/write

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    # Get all query params
    keywords   = request.args.get('keywords', '').strip()
    location   = request.args.get('location', '').strip()
    time_filter = request.args.get('time_filter', '')
    job_type   = request.args.get('job_type', '')
    work_type  = request.args.get('work_type', '')
    experience = request.args.get('experience', '')
    max_results = int(request.args.get('max_results', 60))

    # Check for mandatory fields
    if not keywords or not location:
        return Response("Error: 'keywords' and 'location' are required fields.", status=400)

    jobs_file = 'jobs.json'

    # Clear jobs.json before starting
    with file_lock:
        with open(jobs_file, 'w') as f:
            json.dump([], f)

    q = queue.Queue()

    def worker():
        for job in scrape_jobs_stream(
            keywords, location, time_filter, job_type,
            max_results=max_results,
            work_type=work_type,
            experience=experience
        ):
            # Append job to file safely
            with file_lock:
                try:
                    with open(jobs_file, 'r') as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    data = []

                data.append(job)

                with open(jobs_file, 'w') as f:
                    json.dump(data, f, indent=2)

            # Send to SSE stream
            q.put(job)

        q.put(None)  # Signal end

    # Run scraper in background
    threading.Thread(target=worker, daemon=True).start()

    def event_stream():
        while True:
            job = q.get()
            if job is None:
                break
            yield f"data: {json.dumps(job)}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)
