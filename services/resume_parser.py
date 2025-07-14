import os
import re
import spacy
import fitz  # PyMuPDF
import markdown
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import doctly
import tempfile

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdfjobs.jobs.extract_pdf_job import ExtractPDFJob
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.pdfjobs.params.extract_pdf.extract_pdf_params import ExtractPDFParams
from adobe.pdfservices.operation.pdfjobs.result.extract_pdf_result import ExtractPDFResult

# Load environment variables
load_dotenv()

class ResumeParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

        self.client = doctly.Client(api_key='sk-p16vXStEJvVDEABn2V-juHCz3P6SCqfdUmf1CspCiYDKE9muvoQ-dKQMJ2Hs4eUdj91j')
        self.adobe_credentials = ServicePrincipalCredentials(
            # client_id=os.getenv("PDF_SERVICES_CLIENT_ID"),
            # client_secret=os.getenv("PDF_SERVICES_CLIENT_SECRET")
            client_id="ed85ae5d832f42278e1ff4dfc5d2f201",
            client_secret="p8e-1IX54bleddsKDS1vJgY5pZoa7ltFOMf7"
        )

    def parse_from_pdf(self, pdf_file):
        text = ""
    
    # --- Step 1: Try Doctly ---
        try:
        # Doctly requires a file path string, not a file object
            if isinstance(pdf_file, str):
                text = self.client.process(pdf_file)
            else:
                raise TypeError("Doctly expects file path, not a file object.")
        except Exception as e:
            print(f"Doctly parsing failed: {e}")

    # --- Step 2: Adobe fallback ---
        if not text or len(text.strip()) < 50:
            try:
                text = self.extract_text_using_adobe_api(pdf_file)
            except Exception as e:
                print(f"Adobe parsing failed: {e}")

    # --- Step 3: PyMuPDF fallback ---
        if not text or len(text.strip()) < 50:
            try:
                text = self._extract_text_from_pdf(pdf_file)
            except Exception as e:
                print(f"PyMuPDF failed: {e}")
    
    # --- Step 4: Final fail-safe ---
        if not text or len(text.strip()) < 10:
            print("All text extraction methods failed.")
            return {}

    # --- Proceed to section parsing ---
        try:
            sections = self._identify_sections(text)
            result = {
            "personal_info": self._extract_personal_info(sections.get("personal_info", "")),
            "summary": sections.get("summary", ""),
            "education": self._extract_education(sections.get("education", "")),
            "experience": self._extract_experience(sections.get("experience", "")),
            "skills": self._extract_skills(sections.get("skills", "")),
            "projects": self._extract_projects(sections.get("projects", ""))
        }
            return result
        except Exception as e:
            print(f"Parsing sections failed: {e}")
        return {}


    def extract_text_using_adobe_api(self, pdf_file):
        try:
            from io import BytesIO
            import zipfile
            import json

            pdf_file.seek(0)
            input_stream = pdf_file.read()
            pdf_services = PDFServices(credentials=self.adobe_credentials)
            input_asset = pdf_services.upload(input_stream=input_stream, mime_type=PDFServicesMediaType.PDF)
            extract_pdf_job = ExtractPDFJob(
                input_asset=input_asset,
                extract_pdf_params=ExtractPDFParams(elements_to_extract=[ExtractElementType.TEXT])
            )
            location = pdf_services.submit(extract_pdf_job)
            result: ExtractPDFResult = pdf_services.get_job_result(location, ExtractPDFResult)
            stream_asset: StreamAsset = pdf_services.get_content(result.get_result().get_resource())
            zip_data = BytesIO(stream_asset.get_input_stream())
            with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                for name in zip_ref.namelist():
                    if name.endswith("structuredData.json"):
                        text_json = zip_ref.read(name).decode("utf-8")
                        return self._extract_text_from_adobe_json(json.loads(text_json))
        except Exception as e:
            print(f"Adobe API parsing failed: {e}")
            return ""

    def _extract_text_from_adobe_json(self, json_data):
        """Flatten text from Adobe structured JSON"""
        return "\n".join(
            element.get("Text", "")
            
            for element in json_data.get("elements", [])
            if element.get("Type") == "text"
            
        )

    def _extract_text_from_pdf(self, pdf_file):
        try:
            pdf_file.seek(0)
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            return "\n".join(page.get_text() for page in doc)
        except Exception as e:
            print(f"Fallback PDF parsing failed: {e}")
            return ""

    
    def _extract_projects(self, projects_text):
        """Extract project information from text"""
        projects = []
    
        lines = [line.strip() for line in projects_text.split('\n') if line.strip()]
        current_project = {"title": "", "description": "", "technologies": [], "link": ""}

        for line in lines:
            if line.lower().startswith("technologies:"):
                current_project["technologies"] = [t.strip() for t in line[len("technologies:"):].split(",")]
            elif line.lower().startswith("link:"):
                current_project["link"] = line[len("link:"):].strip()
            elif current_project["title"] == "":
                current_project["title"] = line
            elif current_project["description"] == "":
                current_project["description"] = line
            else:
            # New project start
                projects.append(current_project)
                current_project = {"title": line, "description": "", "technologies": [], "link": ""}

        if current_project["title"]:
            projects.append(current_project)

        return projects

    
    
    def _identify_sections(self, text):
        section_headers = [
            "personal information", "contact", "profile", "summary", "objective",
            "education", "experience", "work experience", "employment", "skills",
            "technical skills", "projects", "achievements", "certifications",
            "extracurricular", "volunteer", "publications", "courses"
        ]
        sections, lines = {}, text.split('\n')
        current_section = "personal_info"
        section_content = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue
            is_header = False
            for header in section_headers:
                if line.strip().lower().startswith(header.lower()):
                    sections[current_section] = section_content.strip()
                    if "personal" in header or "contact" in header:
                        current_section = "personal_info"
                    elif "summary" in header or "objective" in header or "profile" in header:
                        current_section = "summary"
                    elif "education" in header:
                        current_section = "education"
                    elif "experience" in header or "employment" in header:
                        current_section = "experience"
                    elif "skill" in header:
                        current_section = "skills"
                    elif "project" in header:
                        current_section = "projects"
                    else:
                        current_section = header.lower().replace(" ", "_")
                    section_content = ""
                    is_header = True
                    break
            if not is_header:
                section_content += line + "\n"

        sections[current_section] = section_content.strip()
        return sections

    def _extract_personal_info(self, personal_info_text):
        personal_info = {
        "full_name": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": "",
        "portfolio": ""
    }

        lines = [line.strip() for line in personal_info_text.split("\n") if line.strip()]

    # Case 1: "Name • Email • Phone • Location"
        if lines and "•" in lines[0]:
            parts = [p.strip() for p in lines[0].split("•")]
            for part in parts:
                if "@" in part:
                    personal_info["email"] = part
                elif re.search(r"\d{10}", part):
                    personal_info["phone"] = part
                elif not personal_info["full_name"]:
                    personal_info["full_name"] = part
                else:
                    personal_info["location"] = part

    # ✅ Case 2: 4 lines — name, email, phone, location
        elif len(lines) >= 4:
            personal_info["full_name"] = lines[0]
        if "@" in lines[1]: personal_info["email"] = lines[1]
        if re.search(r"\d{10}", lines[2]): personal_info["phone"] = lines[2]
        personal_info["location"] = lines[3]

    # Scan for LinkedIn and GitHub
        full_text = "\n".join(lines)
        linkedin_match = re.search(r"linkedin\.com/in/[a-zA-Z0-9_-]+", full_text)
        github_match = re.search(r"github\.com/[a-zA-Z0-9_-]+", full_text)
        if linkedin_match:
            personal_info["linkedin"] = "https://" + linkedin_match.group(0)
        if github_match:
                personal_info["github"] = "https://" + github_match.group(0)

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
            # Handle formats like: "JNTUH — Bachelors, Computer Science (2019-06-10 – 2023-07-19)"
            alt_date_pattern = r"\((\d{4}-\d{2}-\d{2})\s*[–-]\s*(\d{4}-\d{2}-\d{2}|Present|present|Current|current)\)"
            for line in lines:
                alt_date_match = re.search(alt_date_pattern, line)
                if alt_date_match:
                    try:
                        education["start_date"] = datetime.strptime(alt_date_match.group(1), "%Y-%m-%d").date()
                    except ValueError:
                        pass
                    if alt_date_match.group(2).lower() not in ["present", "current"]:
                        try:
                            education["end_date"] = datetime.strptime(alt_date_match.group(2), "%Y-%m-%d").date()
                        except ValueError:
                            pass


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
    
    def _extract_skills(self, text):
        skills = []
        for item in re.split(r",|\n", text):
            item = item.strip()
            if item:
                category = "technical"
                if any(lang in item.lower() for lang in ["english", "french"]):
                    category = "language"
                elif any(soft in item.lower() for soft in ["communication", "teamwork"]):
                    category = "soft"
                skills.append({"name": item, "category": category, "level": "intermediate"})
        return skills
    

  

# for testing
if __name__ == "__main__":
    parser = ResumeParser()
    
    #  For Doctly
    result = parser.parse_from_pdf("C:/RRP2/software developer resume.pdf")
    print("Parsed:", result)

    result = parser.parse_from_pdf("C:/RRP2/ats_version.pdf")
    print("Parsed:", result)