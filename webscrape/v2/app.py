# app.py
from flask import Flask, render_template, request, Response
import json
import os
from scraper import scrape_jobs_generator

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    # get form args
    kw   = request.args.get('keywords', '')
    loc  = request.args.get('location', '')
    tf   = request.args.get('time_filter', 'any')
    jt   = request.args.get('job_type', '')
    maxr = int(request.args.get('max_results', 60))

    # clear or create jobs.json
    with open('jobs.json', 'w') as f:
        json.dump([], f)

    def event_stream():
        for job in scrape_jobs_generator(kw, loc, tf, jt, maxr):
            # append to JSON file
            data = json.load(open('jobs.json'))
            data.append(job)
            with open('jobs.json','w') as f:
                json.dump(data, f, indent=2)

            # push via SSE
            yield f"data: {json.dumps(job)}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)
