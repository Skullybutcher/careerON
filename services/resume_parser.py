import os
import re
import fitz  # PyMuPDF, you may need to run: pip install PyMuPDF
import base64
from dotenv import load_dotenv  # you may need to run: pip install python-dotenv
from google import genai
from google.genai import types
import uuid
import json
from io import BytesIO

# Load environment variables from a .env file
load_dotenv()

class ResumeParser:
    """
    A class to parse resume files (PDF) using the Gemini API with a fallback
    to local text extraction, outputting in a detailed, structured JSON format.
    """
    def __init__(self):
        """Initializes the parser and creates the Gemini client."""
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")
        
        # Initialize the Gemini client using the modern API pattern
        self.client = genai.Client()

    def parse_from_pdf(self, pdf_file):
        """
        Parses a PDF resume, first by attempting to use the Gemini API,
        and then falling back to a local text extraction method if the API call fails.

        Args:
            pdf_file (str or file-like object): The path to the PDF file or a file-like object.

        Returns:
            dict: A dictionary containing the parsed resume data.
        """
        pdf_data = None

        # --- Step 1: Try parsing with Gemini API ---
        try:
            print("Attempting to parse with the Gemini API...")
            if isinstance(pdf_file, str):
                with open(pdf_file, "rb") as f:
                    pdf_data = f.read()
            else:
                pdf_file.seek(0)
                pdf_data = pdf_file.read()

            # --- MODIFIED PROMPT ---
            # The instructions now strongly enforce the YYYY-MM-DD date format.
            prompt = """You are an expert resume parser. Your task is to analyze the provided resume document and extract its content into a single, structured JSON object that conforms to the detailed format below.

Instructions:
1. Parse the entire resume document for all sections.
2. Populate all fields for each section as specified in the JSON format.
3. **Crucially, all dates in the education section (start_date, end_date) MUST be in YYYY-MM-DD format. If only the month and year are available, default the day to '01' (e.g., 'September 2018' becomes '2018-09-01').**
4. If a specific piece of information is not available, use an empty string "" for text fields, an empty list [] for arrays, or `null` for non-string fields like dates or booleans where appropriate.
5. The final output must be only the JSON text, with no additional explanations.

JSON Output Format:
{
  "personal_info": {
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "location": "San Francisco, CA",
    "linkedin": "https://linkedin.com/in/johndoe",
    "github": "https://github.com/johndoe",
    "portfolio": "https://johndoe.dev"
  },
  "summary": "Experienced software engineer with 5+ years of expertise...",
  "education": [
    {
      "institution": "Stanford University",
      "degree": "Bachelor of Science",
      "field_of_study": "Computer Science",
      "start_date": "2018-09-01",
      "end_date": "2022-06-15",
      "gpa": 3.8,
      "description": "Relevant coursework: Data Structures, Algorithms, Machine Learning"
    }
  ],
  "experience": [
    {
      "company": "Tech Innovations Inc.",
      "position": "Senior Software Engineer",
      "location": "San Francisco, CA",
      "start_date": "2022-07-01",
      "end_date": null,
      "current": true,
      "description": "Lead development of microservices architecture...",
      "achievements": [
        "Improved system performance by 40%",
        "Led team of 5 developers"
      ]
    }
  ],
  "skills": [
    {
      "name": "Python",
      "category": "Programming Languages",
      "proficiency": "Expert"
    }
  ],
  "projects": [
    {
      "name": "AI Resume Optimizer",
      "description": "Machine learning application that optimizes resumes...",
      "technologies": ["Python", "TensorFlow", "Flask"],
      "link": "https://github.com/johndoe/resume-optimizer",
      "start_date": "2023-01-01",
      "end_date": "2023-06-30"
    }
  ]
}
"""

            # Convert PDF to base64 for proper file upload
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

            # Create proper content structure using types
            contents = [
                types.Part(text=prompt),
                types.Part(inline_data=types.Blob(
                    mime_type="application/pdf",
                    data=pdf_base64
                ))
            ]

            # Configure generation settings
            cfg = types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=4000,
                top_p=0.9,
                top_k=40
            )

            # Use the modern Gemini API pattern
            response = self.client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=contents, 
                config=cfg
            )
            
            raw_response_text = response.text
            json_start = raw_response_text.find('{')
            json_end = raw_response_text.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                clean_json_text = raw_response_text[json_start:json_end]
                print("Successfully parsed with Gemini API.")
                return json.loads(clean_json_text)
            else:
                raise Exception("Could not find a valid JSON object in the Gemini response.")

        except Exception as e:
            print(f"Gemini parsing failed: {e}")
            print("Attempting fallback parsing...")

        # --- Step 2: PyMuPDF fallback if Gemini fails ---
        try:
            if pdf_data is None:
                raise Exception("PDF data is not available for fallback.")
                
            pdf_file_obj = BytesIO(pdf_data)
            text = self._extract_text_from_pdf(pdf_file_obj)
            if not text or len(text.strip()) < 20:
                raise Exception("Fallback text extraction yielded very little or no content.")

            # The structure of this dictionary reflects the new detailed format.
            parsed_data = {
                "personal_info": self._extract_personal_info(text),
                "summary": self._extract_summary(text),
                "education": self._extract_education(text),
                "experience": self._extract_experience(text),
                "skills": self._extract_skills(text),
                "projects": self._extract_projects(text)
            }
            print("Successfully parsed with fallback method.")
            return parsed_data

        except Exception as e:
            print(f"Fallback parsing also failed: {e}")
            return {"error": "Both Gemini and fallback parsing failed.", "details": str(e)}

    def _extract_text_from_pdf(self, pdf_file_obj):
        try:
            pdf_file_obj.seek(0)
            doc = fitz.open(stream=pdf_file_obj.read(), filetype="pdf")
            return "\n".join(page.get_text() for page in doc)
        except Exception as e:
            print(f"Error during PyMuPDF text extraction: {e}")
            return ""

    # --- UPDATED PLACEHOLDER METHODS FOR FALLBACK LOGIC ---

    def _extract_personal_info(self, text):
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
        return {
            "full_name": "N/A (Fallback)",
            "email": email_match.group(0) if email_match else "",
            "phone": "",
            "location": "",
            "linkedin": "",
            "github": "",
            "portfolio": ""
        }

    def _extract_summary(self, text):
        return "Summary not extracted by fallback."

    def _extract_education(self, text):
        # Your logic here should find and format dates to 'YYYY-MM-DD'.
        return []

    def _extract_experience(self, text):
        return []

    def _extract_skills(self, text):
        return []

    def _extract_projects(self, text):
        return []


if __name__ == "__main__":
    parser = ResumeParser()
    
    # IMPORTANT: Set the path to your test PDF file.
    file_path = "C:/Users/ayush/Documents/careerON/services/For_Internships.pdf"
    
    if os.path.exists(file_path):
        result = parser.parse_from_pdf(file_path)
        
        print("\n--- Final Parsed Result ---")
        print(json.dumps(result, indent=4))
    else:
        print(f"Error: The file was not found at the specified path: {file_path}")
        print("Please update the 'file_path' variable in the if __name__ == '__main__': block.")
