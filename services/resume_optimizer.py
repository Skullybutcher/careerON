import spacy
import os
import json
import re

from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import datetime
#import google.generativeai as genai
from google import genai
from google.genai import types
class ResumeOptimizer:
    def __init__(self):
        #genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
       # self.gemini_model = genai.GenerativeModel(model_name="gemini-2.5-flash-lite")
       
        # The client gets the API key from the environment variable `GEMINI_API_KEY`.
        self.client = genai.Client()


        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
<<<<<<< HEAD
        self.hf_client = InferenceClient("HuggingFaceH4/zephyr-7b-beta", token=os.getenv("HF_TOKEN"))
=======
        self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
>>>>>>> a2ae794 (Fix: optimized resume optimization)

    def optimize_for_job(self, resume, job_description):
        resume_text = self._get_resume_text(resume)

        resume_embedding = self.embedder.encode(resume_text, convert_to_tensor=True)
        job_embedding = self.embedder.encode(job_description, convert_to_tensor=True)

        similarity_score = util.pytorch_cos_sim(resume_embedding, job_embedding).item()

        resume_skills = self._extract_skills_with_nlp(resume_text)
        job_skills = self._extract_skills_with_nlp(job_description)
        missing_skills = list(job_skills - resume_skills)

        suggestions = self._generate_suggestions(resume, missing_skills)
        optimized_summary = self._optimize_summary(resume, job_description)

        return {
            "score": similarity_score,
            "feedback": self._get_feedback_category(similarity_score),
            "suggestions": suggestions,
            "optimized_summary": optimized_summary,
            "missing_skills": missing_skills,
           "resume_boost_paragraph": self._generate_resume_boost_paragraph(missing_skills, job_description)
        }

    def enhance_resume(self, resume, ats_result, keyword_matches):
        ats_issues = "\n".join(f"- {i}" for i in ats_result['issues']) or "None"
        missing = [k for k, v in keyword_matches.items() if v < 0.5]
        missing_text = ", ".join(missing[:10]) or "None"
        #print(f"Prompt length: {len(prompt)} characters")

        def custom_serializer(obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        prompt = f"""
You are a resume coach AI. Please provide suggestions to improve the following resume based on detected ATS issues and missing keywords.

ATS Issues:
{ats_issues}

Missing Keywords:
{missing_text}

Resume JSON:
{json.dumps(resume, indent=2, default=custom_serializer)}

Instructions:
Give concise feedback using the following format:

Summary Advice:
...

Skills Advice:
...

Projects Advice:
...

Keep each section under 4 lines. Use plain text only. No commentary.
"""


        response = self._generate_with_gemini(prompt)

        # Extract structured advice with regex
        summary = re.search(r"Summary Advice:\s*(.*?)(Skills Advice:|Projects Advice:|$)", response, re.DOTALL)
        skills = re.search(r"Skills Advice:\s*(.*?)(Projects Advice:|$)", response, re.DOTALL)
        projects = re.search(r"Projects Advice:\s*(.*)", response, re.DOTALL)

        return {
            "summary_advice": (summary.group(1).strip() if summary else ""),
            "skills_advice": (skills.group(1).strip() if skills else ""),
            "projects_advice": (projects.group(1).strip() if projects else "")
        }





    def _generate_with_gemini(self, prompt: str) -> str:
    # client should already be attached to self; just showing instantiation here
        client = genai.Client()

        cfg = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig( thinking_budget=0 ),  # disables “thinking”
            temperature=0.7,
            max_output_tokens=350,
            top_p=0.9,
            top_k=40
    )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,      
            config=cfg
        )

        return response.text




    def _get_resume_text(self, resume):
        sections = []
        if resume.get("summary"):
            sections.append(resume["summary"])
        for exp in resume.get("experience", []):
            sections.append(exp.get("description", ""))
            sections.extend(exp.get("achievements", []))
        skills = [skill["name"] for skill in resume.get("skills", [])]
        sections.append(" ".join(skills))
        for project in resume.get("projects", []):
            sections.append(project.get("description", ""))
            if project.get("technologies"):
                sections.append(" ".join(project["technologies"]))
        return " ".join(sections)

    def _extract_skills_with_nlp(self, text):
        doc = self.nlp(text)
        tokens = set(
            token.text.lower()
            for token in doc
            if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 2
        )
        return tokens

    def _generate_suggestions(self, resume, missing_skills):
        suggestions = []
        if missing_skills:
            suggestions.append(f"Consider adding the following skills to align with the job requirements: {', '.join(missing_skills)}.")
        if not resume.get("summary"):
            suggestions.append("Add a professional summary to highlight your key qualifications.")
        if len(resume.get("skills", [])) < 5:
            suggestions.append("Include more relevant skills to showcase your expertise.")
        return suggestions

    def _check_ats_compatibility(self, resume):
        suggestions = []
        personal_info = resume.get("personal_info", {})
        if not personal_info.get("phone") or not personal_info.get("email"):
            suggestions.append("Ensure your resume includes complete contact information (phone and email).")
        if not resume.get("education"):
            suggestions.append("Add an education section to your resume.")
        section_settings = resume.get("section_settings", [])
        required_sections = ["summary", "experience", "education", "skills"]
        for section in required_sections:
            if section not in [s["name"] for s in section_settings if s.get("visible", True)]:
                suggestions.append(f"Make sure your resume includes a visible {section} section.")
        return suggestions

    def _optimize_summary(self, resume, job_description):
        if not resume.get("summary"):
            skills = ", ".join([skill["name"] for skill in resume.get("skills", [])][:5])
            experience = next((exp["position"] for exp in resume.get("experience", [])), "")
            return f"Experienced professional with expertise in {skills}. Proven track record as {experience} seeking to leverage skills and experience in a new role."
        return resume.get("summary")

    def _get_feedback_category(self, score):
        if score >= 0.85:
            return "Excellent match"
        elif score >= 0.70:
            return "Good match with minor improvements"
        else:
            return "Needs significant improvements"

    def _generate_resume_boost_paragraph(self, missing_skills, job_description=None):
        if not missing_skills:
            return "Your resume already highlights the core skills needed for this job!"
        skills_sentence = ", ".join(missing_skills[:5])
        prompt = (
            f"Write a concise, energetic resume summary paragraph that highlights proficiency in the following skills: {skills_sentence}. "
            f"{'Here is the job description for context: ' + job_description if job_description else ''} "
            "Do not mention technologies or skills not listed. Focus on making the candidate sound like a strong fit for the job."
        )
        response = self._generate_with_gemini(prompt)
        return response.strip()
    

    def check_ats_compatibility(self, resume):
        issues = self._check_ats_compatibility(resume)
        return {
            "is_compatible": len(issues) == 0,
            "issues": issues,
            "compatibility_score": 1.0 - (len(issues) * 0.1)
        }
