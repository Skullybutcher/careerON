import PyPDF2
import re
import spacy
from datetime import datetime

class ResumeParser:
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # If model not found, download it
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
    
    def parse_from_pdf(self, pdf_file):
        """Extract text and structure from a PDF resume"""
        
        # Extract text from PDF
        text = self._extract_text_from_pdf(pdf_file)
        
        # Parse sections
        sections = self._identify_sections(text)
        
        # Process each section
        result = {
            "personal_info": self._extract_personal_info(sections.get("personal_info", "")),
            "summary": sections.get("summary", ""),
            "education": self._extract_education(sections.get("education", "")),
            "experience": self._extract_experience(sections.get("experience", "")),
            "skills": self._extract_skills(sections.get("skills", "")),
            "projects": self._extract_projects(sections.get("projects", ""))
        }

    def _extract_projects(self, projects_text):
        """Extract project information from text"""
        projects = []
        
        # Using regex to find project entries
        project_pattern = r"(.*?)(?:\n|$)(?:\s*-\s*(.*?))?(?:\n|$)(?:\s*Technologies:(.*?))?(?:\n|$)(?:\s*Link:(.*?))?(?:\n|$)"
        matches = re.finditer(project_pattern, projects_text)
        
        for match in matches:
            if match.group(1).strip():
                project = {
                    "title": match.group(1).strip(),
                    "description": match.group(2).strip() if match.group(2) else "",
                    "technologies": [tech.strip() for tech in match.group(3).split(",")] if match.group(3) else [],
                    "link": match.group(4).strip() if match.group(4) else ""
                }
                projects.append(project)
        
        return projects
    
    def _extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF file"""
        text = ""
        try:
            reader = PyPDF2.PdfFileReader(pdf_file)
            for page_num in range(reader.numPages):
                text += reader.getPage(page_num).extractText()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
        
        return text
    
    def _identify_sections(self, text):
        """Identify different sections in the resume"""
        # Common section headers
        section_headers = [
            "personal information", "contact", "profile", "summary", "objective",
            "education", "experience", "work experience", "employment", "skills",
            "technical skills", "projects", "achievements", "certifications",
            "extracurricular", "volunteer", "publications", "courses"
        ]
        
        # Initialize sections dictionary
        sections = {}
        
        # Split text into lines
        lines = text.split('\n')
        current_section = "personal_info"  # Default section
        section_content = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a section header
            is_header = False
            for header in section_headers:
                if header.lower() in line.lower() and len(line) < 30:  # Assuming headers are short
                    # Save previous section
                    sections[current_section] = section_content.strip()
                    
                    # Start new section
                    if "personal" in header.lower() or "contact" in header.lower():
                        current_section = "personal_info"
                    elif "summary" in header.lower() or "objective" in header.lower() or "profile" in header.lower():
                        current_section = "summary"
                    elif "education" in header.lower():
                        current_section = "education"
                    elif "experience" in header.lower() or "employment" in header.lower():
                        current_section = "experience"
                    elif "skill" in header.lower():
                        current_section = "skills"
                    elif "project" in header.lower():
                        current_section = "projects"
                    elif "achievement" in header.lower():
                        current_section = "achievements"
                    elif "certification" in header.lower():
                        current_section = "certifications"
                    elif "extracurricular" in header.lower():
                        current_section = "extracurriculars"
                    elif "volunteer" in header.lower():
                        current_section = "volunteer_work"
                    elif "publication" in header.lower():
                        current_section = "publications"
                    elif "course" in header.lower():
                        current_section = "courses"
                    else:
                        current_section = header.lower().replace(" ", "_")
                    
                    section_content = ""
                    is_header = True
                    break
            
            if not is_header:
                section_content += line + "\n"
        
        # Save last section
        sections[current_section] = section_content.strip()
        
        return sections
    
    def _extract_personal_info(self, personal_info_text):
        """Extract personal information"""
        personal_info = {
            "full_name": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin": "",
            "github": "",
            "portfolio": ""
        }
        
        # Extract email
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", personal_info_text)
        if email_match:
            personal_info["email"] = email_match.group(0)
        
        # Extract phone
        phone_match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", personal_info_text)
        if phone_match:
            personal_info["phone"] = phone_match.group(0)
        
        # Extract LinkedIn
        linkedin_match = re.search(r"linkedin\.com/in/[a-zA-Z0-9_-]+", personal_info_text)
        if linkedin_match:
            personal_info["linkedin"] = "https://" + linkedin_match.group(0)
        
        # Extract GitHub
        github_match = re.search(r"github\.com/[a-zA-Z0-9_-]+", personal_info_text)
        if github_match:
            personal_info["github"] = "https://" + github_match.group(0)
        
        # Extract name (this is more complex and less reliable)
        lines = personal_info_text.split('\n')
        if lines and not any(char in lines[0] for char in "@./:"):  # Avoid URLs and emails
            personal_info["full_name"] = lines[0].strip()
        
        # Extract location (also complex)
        location_patterns = [
            r"\b[A-Z][a-z]+,\s*[A-Z]{2}\b",  # City, State
            r"\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b"  # City, Country
        ]
        
        for pattern in location_patterns:
            location_match = re.search(pattern, personal_info_text)
            if location_match:
                personal_info["location"] = location_match.group(0)
                break
        
        return personal_info
    
    def _extract_education(self, education_text):
        """Extract education information"""
        education_entries = []
        
        # Split into different education entries (this is a simplified approach)
        education_blocks = re.split(r"\n\n+", education_text)
        
        for block in education_blocks:
            if not block.strip():
                continue
                
            education = {
                "institution": "",
                "degree": "",
                "field_of_study": "",
                "start_date": None,
                "end_date": None,
                "gpa": None,
                "description": ""
            }
            
            lines = block.split('\n')
            
            # First line is often the institution
            if lines:
                education["institution"] = lines[0].strip()
            
            # Look for degree information
            degree_pattern = r"(Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.E\.|M\.E\.|B\.Tech|M\.Tech|B\.A\.|M\.A\.|M\.B\.A\.).*(in|of)\s+([\w\s]+)"
            for line in lines:
                degree_match = re.search(degree_pattern, line, re.IGNORECASE)
                if degree_match:
                    education["degree"] = degree_match.group(1).strip()
                    education["field_of_study"] = degree_match.group(3).strip()
            
            # Look for dates
            date_pattern = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)[\s,]+(\d{4})\s*[-–]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)[\s,]+(\d{4}|Present|present|Current|current)"
            for line in lines:
                date_match = re.search(date_pattern, line)
                if date_match:
                    start_month, start_year = date_match.group(1), date_match.group(2)
                    end_month, end_year = date_match.group(3), date_match.group(4)
                    
                    try:
                        education["start_date"] = datetime.strptime(f"{start_month} {start_year}", "%B %Y").date()
                    except ValueError:
                        try:
                            education["start_date"] = datetime.strptime(f"{start_month} {start_year}", "%b %Y").date()
                        except ValueError:
                            pass
                    
                    if end_year.lower() not in ["present", "current"]:
                        try:
                            education["end_date"] = datetime.strptime(f"{end_month} {end_year}", "%B %Y").date()
                        except ValueError:
                            try:
                                education["end_date"] = datetime.strptime(f"{end_month} {end_year}", "%b %Y").date()
                            except ValueError:
                                pass
            
            # Look for GPA
            gpa_pattern = r"GPA:?\s*(\d+\.\d+)"
            for line in lines:
                gpa_match = re.search(gpa_pattern, line)
                if gpa_match:
                    education["gpa"] = float(gpa_match.group(1))
            
            education_entries.append(education)
        
        return education_entries
    
    def _extract_experience(self, experience_text):
        """Extract work experience information"""
        experience_entries = []
        
        # Split into different experience entries
        experience_blocks = re.split(r"\n\n+", experience_text)
        
        for block in experience_blocks:
            if not block.strip():
                continue
                
            experience = {
                "company": "",
                "position": "",
                "location": "",
                "start_date": None,
                "end_date": None,
                "current": False,
                "description": "",
                "achievements": []
            }
            
            lines = block.split('\n')
            
            # First line often contains company and position
            if lines:
                company_position = lines[0].split('-')
                if len(company_position) > 1:
                    experience["company"] = company_position[0].strip()
                    experience["position"] = company_position[1].strip()
                else:
                    experience["company"] = lines[0].strip()
            
            # Look for dates and location
            date_loc_pattern = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)[\s,]+(\d{4})\s*[-–]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)[\s,]+(\d{4}|Present|present|Current|current)\s*(?:\||\,)?\s*(.*)"
            for line in lines:
                date_loc_match = re.search(date_loc_pattern, line)
                if date_loc_match:
                    start_month, start_year = date_loc_match.group(1), date_loc_match.group(2)
                    end_month, end_year = date_loc_match.group(3), date_loc_match.group(4)
                    location = date_loc_match.group(5).strip() if date_loc_match.group(5) else ""
                    
                    try:
                        experience["start_date"] = datetime.strptime(f"{start_month} {start_year}", "%B %Y").date()
                    except ValueError:
                        try:
                            experience["start_date"] = datetime.strptime(f"{start_month} {start_year}", "%b %Y").date()
                        except ValueError:
                            pass
                    
                    if end_year.lower() in ["present", "current"]:
                        experience["current"] = True
                    else:
                        try:
                            experience["end_date"] = datetime.strptime(f"{end_month} {end_year}", "%B %Y").date()
                        except ValueError:
                            try:
                                experience["end_date"] = datetime.strptime(f"{end_month} {end_year}", "%b %Y").date()
                            except ValueError:
                                pass
                    
                    experience["location"] = location
            
            # Extract achievements/description
            description_lines = []
            for line in lines[1:]:  # Skip the first line (company/position)
                if not any(pattern in line.lower() for pattern in ["jan ", "feb ", "mar ", "apr ", "may ", "jun ", "jul ", "aug ", "sep ", "oct ", "nov ", "dec "]):
                    description_lines.append(line)
            
            experience["description"] = "\n".join(description_lines).strip()
            
            # Extract bullet points as achievements
            achievement_pattern = r"[-•*]\s*(.*)"
            achievements = []
            for line in description_lines:
                achievement_match = re.search(achievement_pattern, line)
                if achievement_match:
                    achievements.append(achievement_match.group(1).strip())
            
            experience["achievements"] = achievements
            
            experience_entries.append(experience)
        
        return experience_entries
    
    def _extract_skills(self, skills_text):
        """Extract skills"""
        skills = []
        
        # Simple split by comma or newline
        skill_items = re.split(r",|\n", skills_text)
        
        for item in skill_items:
            item = item.strip()
            if item:
                # Try to determine skill category
                category = "technical"  # Default
                if any(lang in item.lower() for lang in ["english", "spanish", "french", "german", "chinese", "japanese"]):
                    category = "language"
                elif any(soft in item.lower() for soft in ["communication", "leadership", "teamwork", "problem solving", "critical thinking"]):
                    category = "soft"
                
                skills.append({
                    "name": item,
                    "category": category,
                    "level": "intermediate"  # Default level, hard to determine from text
                })
        
        return skills
    
    def parse_from_linkedin(self, linkedin_url):
        """Parse resume from LinkedIn profile"""
        # This would require implementing a LinkedIn scraper
        # which is beyond the scope of this example
        raise NotImplementedError("LinkedIn parsing not implemented")
