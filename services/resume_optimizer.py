import spacy
import os
import json
import re
from sentence_transformers import SentenceTransformer, util
from huggingface_hub import InferenceClient

class ResumeOptimizer:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.hf_client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.1", token=os.getenv("HF_TOKEN"))

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
            "resume_boost_paragraph": self._generate_resume_boost_paragraph(missing_skills)
        }

    def enhance_resume(self, resume, ats_result, keyword_matches):
        ats_issues = "\n".join(f"- {i}" for i in ats_result['issues']) or "None"
        missing = [k for k, v in keyword_matches.items() if v < 0.5]
        missing_text = ", ".join(missing[:10]) or "None"

        prompt = f"""
You are an expert resume writer. Improve the provided resume JSON for better ATS compatibility and human readability, focusing on these ATS issues and missing keywords:

ATS Issues:
{ats_issues}

Keyword Gaps:
{missing_text}

Original Resume:
{json.dumps(resume, indent=2)}

Please output only the enhanced resume as JSON in the same schema.
"""

        response = self.hf_client.text_generation(prompt, max_new_tokens=1500, temperature=0.2)

        try:
            return json.loads(response)
        except Exception:
            match = re.search(r"(\{.*\})", response, re.DOTALL)
            return json.loads(match.group(1)) if match else {}

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
            suggestions.append("Consider adding these skills to your resume: " + ", ".join(missing_skills[:5]))

        if not resume.get("summary"):
            suggestions.append("Add a professional summary that highlights your relevant skills and experience.")

        if len(resume.get("skills", [])) < 5:
            suggestions.append("Add more skills relevant to the job description.")

        achievement_count = sum(len(exp.get("achievements", [])) for exp in resume.get("experience", []))
        if achievement_count < 3:
            suggestions.append("Add more achievement statements to your work experience using action verbs and quantifiable results.")

        suggestions.extend(self._check_ats_compatibility(resume))

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

    def _generate_resume_boost_paragraph(self, missing_skills):
        if not missing_skills:
            return "Your resume already highlights the core skills needed for this job!"
        skills_sentence = ", ".join(missing_skills[:5])
        return f"Proficient in {skills_sentence}, with hands-on experience in modern full-stack development practices and cloud-native technologies."

    def check_ats_compatibility(self, resume):
        issues = self._check_ats_compatibility(resume)
        return {
            "is_compatible": len(issues) == 0,
            "issues": issues,
            "compatibility_score": 1.0 - (len(issues) * 0.1)
        }
