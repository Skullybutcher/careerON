import spacy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class ResumeOptimizer:
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # If model not found, download it
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        self.vectorizer = CountVectorizer(stop_words='english')
    
    def optimize_for_job(self, resume, job_description):
        """Optimize resume for a specific job description"""
        # Extract key sections from resume
        resume_text = self._get_resume_text(resume)
        
        # Extract keywords from job description
        job_keywords = self._extract_keywords(job_description)
        
        # Calculate keyword matches
        keyword_matches = self._calculate_keyword_matches(resume_text, job_keywords)
        
        # Calculate overall score
        score = sum(keyword_matches.values()) / len(keyword_matches) if keyword_matches else 0
        
        # Generate improvement suggestions
        suggestions = self._generate_suggestions(resume, job_description, keyword_matches)
        
        # Optimize summary
        optimized_summary = self._optimize_summary(resume, job_description)
        
        return {
            "score": score,
            "suggestions": suggestions,
            "optimized_summary": optimized_summary,
            "keyword_matches": keyword_matches
        }
    
    def _get_resume_text(self, resume):
        """Extract text from resume sections"""
        sections = []
        
        # Add summary
        if resume.get("summary"):
            sections.append(resume["summary"])
        
        # Add experience descriptions
        for exp in resume.get("experience", []):
            sections.append(exp.get("description", ""))
            sections.extend(exp.get("achievements", []))
        
        # Add skills
        skills = [skill["name"] for skill in resume.get("skills", [])]
        sections.append(" ".join(skills))
        
        # Add projects
        for project in resume.get("projects", []):
            sections.append(project.get("description", ""))
            if project.get("technologies"):
                sections.append(" ".join(project["technologies"]))
        
        return " ".join(sections)
    
    def _extract_keywords(self, text):
        """Extract important keywords from text"""
        doc = self.nlp(text)
        
        # Extract noun phrases, technical terms, and named entities
        keywords = []
        
        # Get noun phrases
        for chunk in doc.noun_chunks:
            keywords.append(chunk.text.lower())
        
        # Get named entities
        for ent in doc.ents:
            keywords.append(ent.text.lower())
        
        # Get technical terms (simplified approach)
        tech_patterns = [
            r"\b(?:Python|Java|C\+\+|JavaScript|React|Angular|Vue|Node\.js|Django|Flask|SQL|NoSQL|MongoDB|PostgreSQL|AWS|Azure|DevOps|Docker|Kubernetes|CI/CD|ML|AI|NLP|data science|cloud)\b",
            r"\b(?:software|develop|engineer|program|code|test|debug|deploy|maintain|design|architect|implement|optimize|scale)\w*\b"
        ]
        
        for pattern in tech_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                keywords.append(match.group(0).lower())
        
        # Remove duplicates and very common words
        filtered_keywords = []
        stopwords = ["the", "and", "a", "an", "in", "on", "at", "of", "to", "for", "with", "by"]
        
        for keyword in keywords:
            keyword = keyword.strip()
            if (
                keyword and 
                keyword not in stopwords and 
                len(keyword) > 2 and 
                keyword not in filtered_keywords
            ):
                filtered_keywords.append(keyword)
        
        return filtered_keywords
    
    def _calculate_keyword_matches(self, resume_text, job_keywords):
        """Calculate how many job keywords are present in the resume"""
        resume_text = resume_text.lower()
        
        # Check for each keyword
        matches = {}
        for keyword in job_keywords:
            # Look for exact matches or stems
            if re.search(r"\b" + re.escape(keyword) + r"\b", resume_text):
                matches[keyword] = 1.0
            elif re.search(r"\b" + re.escape(keyword[:-1]) + r"\b", resume_text):  # Simple stemming
                matches[keyword] = 0.8
            else:
                matches[keyword] = 0.0
        
        return matches
    
    def _generate_suggestions(self, resume, job_description, keyword_matches):
        """Generate improvement suggestions based on keyword matches"""
        suggestions = []
        
        # Missing keywords suggestions
        missing_keywords = [k for k, v in keyword_matches.items() if v < 0.5]
        if missing_keywords:
            important_missing = missing_keywords[:5]  # Limit to 5 most important
            suggestions.append(f"Consider adding these keywords to your resume: {', '.join(important_missing)}")
        
        # Section-specific suggestions
        if not resume.get("summary"):
            suggestions.append("Add a professional summary that highlights your relevant skills and experience")
        
        if len(resume.get("skills", [])) < 5:
            suggestions.append("Add more skills relevant to the job description")
        
        # Check achievement statements in experience
        achievement_count = sum(len(exp.get("achievements", [])) for exp in resume.get("experience", []))
        if achievement_count < 3:
            suggestions.append("Add more achievement statements to your work experience using action verbs and quantifiable results")
        
        # Check for ATS compatibility
        suggestions.extend(self._check_ats_compatibility(resume))
        
        return suggestions
    
    def _check_ats_compatibility(self, resume):
        """Check resume for ATS compatibility issues"""
        suggestions = []
        
        # Check for sufficient contact information
        personal_info = resume.get("personal_info", {})
        if not personal_info.get("phone") or not personal_info.get("email"):
            suggestions.append("Ensure your resume includes complete contact information (phone and email)")
        
        # Check for education section
        if not resume.get("education"):
            suggestions.append("Add an education section to your resume")
        
        # Check for appropriate sections and ordering
        section_settings = resume.get("section_settings", [])
        required_sections = ["summary", "experience", "education", "skills"]
        
        for section in required_sections:
            if section not in [s["name"] for s in section_settings if s.get("visible", True)]:
                suggestions.append(f"Make sure your resume includes a visible {section} section")
        
        return suggestions
    
    def _optimize_summary(self, resume, job_description):
        """Generate an optimized professional summary"""
        if not resume.get("summary"):
            skills = ", ".join([skill["name"] for skill in resume.get("skills", [])][:5])
            experience = next((exp["position"] for exp in resume.get("experience", [])), "")
            
            return f"Experienced professional with expertise in {skills}. " + \
                   f"Proven track record as {experience} seeking to leverage skills and experience in a new role."
        
        # If summary exists, we would use more sophisticated NLP techniques to improve it
        # but for simplicity, we're returning the existing summary
        return resume.get("summary")
    
    def check_ats_compatibility(self, resume):
        """Check if resume is ATS compatible"""
        issues = self._check_ats_compatibility(resume)
        
        return {
            "is_compatible": len(issues) == 0,
            "issues": issues,
            "compatibility_score": 1.0 - (len(issues) * 0.1)  # Simple scoring
        }