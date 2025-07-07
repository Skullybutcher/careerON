import os
import json
import re
from datetime import datetime, date

import spacy
import torch
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz  # Replaces fuzzywuzzy

from google import genai
from google.genai import types


class ResumeOptimizer:
    def __init__(self):
        self.client = genai.Client()
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

    def optimize_for_job(self, resume, job_description):
        resume_text = self._get_resume_text(resume)

        resume_embedding = self.embedder.encode(resume_text, convert_to_tensor=True)
        job_embedding = self.embedder.encode(job_description, convert_to_tensor=True)
        similarity_score = util.pytorch_cos_sim(resume_embedding, job_embedding).item()

        resume_skills = self._extract_skills_with_nlp(resume_text)
        job_skills = self._extract_skills_with_nlp(job_description)
        missing_skills = self._find_missing_skills(resume_skills, job_skills)

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

        prompt = self._build_advice_prompt(resume, ats_issues, missing_text)
        response = self._generate_with_gemini(prompt)

        return self._extract_advice_from_response(response)

    def check_ats_compatibility(self, resume):
        issues = self._check_ats_compatibility(resume)
        return {
            "is_compatible": len(issues) == 0,
            "issues": issues,
            "compatibility_score": 1.0 - (len(issues) * 0.1)
        }

    # ------------------ Internal Methods ------------------

    def _get_resume_text(self, resume):
        sections = []
        sections.append(resume.get("summary", ""))
        for exp in resume.get("experience", []):
            sections.append(exp.get("description", ""))
            sections.extend(exp.get("achievements", []))
        skills = [s["name"] for s in resume.get("skills", [])]
        sections.append(" ".join(skills))
        for project in resume.get("projects", []):
            sections.append(project.get("description", ""))
            sections.append(" ".join(project.get("technologies", [])))
        return " ".join(sections)

    def _extract_skills_with_nlp(self, text):
        doc = self.nlp(text)
        return set(token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 2)

    def _find_missing_skills(self, resume_skills, job_skills, threshold=85):
        missing = []
        for job_skill in job_skills:
            match_found = any(fuzz.ratio(job_skill, res_skill) >= threshold for res_skill in resume_skills)
            if not match_found:
                missing.append(job_skill)
        return missing

    def _generate_suggestions(self, resume, missing_skills):
        suggestions = []
        if missing_skills:
            suggestions.append("Add these skills: " + ", ".join(missing_skills))
        if not resume.get("summary"):
            suggestions.append("Add a professional summary.")
        if len(resume.get("skills", [])) < 5:
            suggestions.append("Include more relevant skills.")
        return suggestions

    def _check_ats_compatibility(self, resume):
        suggestions = []
        if not resume.get("personal_info", {}).get("email") or not resume.get("personal_info", {}).get("phone"):
            suggestions.append("Include phone and email in contact details.")
        if not resume.get("education"):
            suggestions.append("Add education section.")
        required = ["summary", "experience", "education", "skills"]
        visible_sections = [s["name"] for s in resume.get("section_settings", []) if s.get("visible", True)]
        for section in required:
            if section not in visible_sections:
                suggestions.append(f"Ensure {section} section is visible.")
        return suggestions

    def _optimize_summary(self, resume, job_description):
        if resume.get("summary"):
            return resume["summary"]
        skills = ", ".join([s["name"] for s in resume.get("skills", [])][:5])
        position = next((exp["position"] for exp in resume.get("experience", [])), "")
        return f"Experienced professional with skills in {skills}, seeking a role as {position}."

    def _get_feedback_category(self, score):
        if score >= 0.85:
            return "Excellent match"
        elif score >= 0.70:
            return "Good match with minor improvements"
        return "Needs significant improvements"

    def _generate_resume_boost_paragraph(self, missing_skills, job_description):
        if not missing_skills:
            return "Your resume already highlights the key skills!"
        skills_list = ", ".join(missing_skills[:5])
        prompt = (
            f"Write a strong resume summary using these skills: {skills_list}. "
            f"{'Job Description: ' + job_description if job_description else ''} "
            "Avoid irrelevant technologies. Be concise and persuasive."
        )
        return self._generate_with_gemini(prompt).strip()

    def _generate_with_gemini(self, prompt):
        cfg = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            temperature=0.7,
            max_output_tokens=350,
            top_p=0.9,
            top_k=40
        )
        response = self.client.models.generate_content(model="gemini-2.5-flash", contents=prompt, config=cfg)
        return response.text

    def _build_advice_prompt(self, resume, ats_issues, missing_keywords):
        def custom_serializer(obj):
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        resume_json = json.dumps(resume, indent=2, default=custom_serializer)

        return f"""
You are a resume coach AI. Provide suggestions to improve this resume:

ATS Issues:
{ats_issues}

Missing Keywords:
{missing_keywords}

Resume JSON:
{resume_json}

Output:
Summary Advice:
...

Skills Advice:
...

Projects Advice:
...
"""

    def _extract_advice_from_response(self, response):
        def extract(section):
            match = re.search(rf"{section}:\s*(.*?)(\n[A-Z][a-z]+ Advice:|$)", response, re.DOTALL)
            return match.group(1).strip() if match else ""

        return {
            "summary_advice": extract("Summary Advice"),
            "skills_advice": extract("Skills Advice"),
            "projects_advice": extract("Projects Advice")
        }
