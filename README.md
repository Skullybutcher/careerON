# CareerON - Career Opportunities Navigator

## 🚀 Project Overview

CareerON is an AI-powered resume builder and optimizer that helps job seekers create, refine, and export professional resumes tailored to specific job roles. With features like PDF resume parsing, ATS compatibility analysis, and Gemini-based optimization, CareerON is a smart assistant for your career.

---

## 🔧 Features

### 🗂️ Resume Management

* Create and manage multiple resumes.
* Drag-and-drop to reorder resume sections.
* Toggle visibility for specific resume sections.

### 📄 PDF Resume Parsing

* Upload your existing PDF resume.
* Extracts structured data: personal info, education, skills, projects, etc.
* Uses `PyMuPDF` with NLP heuristics for higher accuracy.

### 🧠 AI-Powered Optimization

* Paste a job description and get:

  * Match Score
  * Missing keywords
  * Summary optimization
  * Section-wise advice (Summary, Skills, Projects)
  * Resume boost paragraph for job-specific tailoring
* Powered by Gemini 2.5 Flash

### 🚪 Export Options

* Export resumes to PDF using professional templates.
* Choose between `default` and `modern` HTML-based templates.

### 🛍️ User Authentication

* Secure login and registration
* JWT-based auth system

---

## 🧰 Tech Stack

### Backend

* Python 3.10+
* Flask
* SQLAlchemy ORM
* PyJWT (Auth)
* PyMuPDF (PDF parsing)
* spaCy (NLP)
* SentenceTransformers (Semantic similarity)
* Gemini 2.5 Flash (Text generation)

### Frontend

* Vue.js 3 (Vite + Composition API)
* TailwindCSS
* Axios
* Toast notifications
* Fully responsive and dynamic

### Database

* PostgreSQL (Production)
* SQLite (Local development)

---

## 📊 Architecture

```
Frontend (Vue.js) ↔ Flask API ↔ PostgreSQL
                            ↕
                AI Services: Gemini | spaCy | PyMuPDF | SentenceTransformers
```

---

## ⚡ Quickstart

### 🔄 Clone & Setup Backend

```bash
git clone https://github.com/Skullybutcher/careerON.git
cd careerON
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### ⚖️ Configure Environment

Copy `.env.example` to `.env` and fill:

```
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost/career_navigator
GEMINI_API_KEY=your_google_ai_key_here
SECRET_KEY=your_jwt_secret
```

### 📝 Create DB

```bash
psql -U youruser -c "CREATE DATABASE career_navigator;"
```

### 🚀 Run the App

```bash
flask run
# Visit: http://localhost:5000
```

---

## 📊 Folder Structure

```
careerON/
├── api/               # Flask API routes & schemas
├── database/          # SQLAlchemy models & db connection
├── services/          # Resume parsing, generation, optimization
├── static/            # CSS/JS assets
├── templates/         # HTML resume templates
├── config.py          # Env config
├── app.py             # Entry point
├── requirements.txt
└── README.md
```

---

## 📃 Example Usage

### Resume Optimization Endpoint

```http
POST /resumes/<resume_id>/optimize
Body: {
  "job_description": "Paste full JD here"
}
```

Response includes:

* `match_score`
* `missing_skills`
* `optimized_summary`
* `summary_advice`, `skills_advice`, `projects_advice`
* `resume_boost_paragraph`

---

## 💼 Planned Enhancements

* ✏️ OCR-based fallback for non-digital PDFs
* 🧠 LLM-driven structured resume builder
* ✨ More export templates and themes
* 👥 Team mode for collaborative resume editing
* 🔍 ElasticSearch for job recommendation

---

## 🙌 Contributing

PRs welcome 🚀

1. Fork & clone
2. Create feature branch
3. Submit PR with meaningful commit messages

---



## Ⓜ️ License

MIT - See [LICENSE](LICENSE)

---

## 🔗 Links

* Live app: \[Coming Soon]
* API Docs: \[docs/README.md]
