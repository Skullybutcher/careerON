import pdfkit
import jinja2
import os
from datetime import datetime

class ResumeGenerator:
    def __init__(self):
        # Template environment
        template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def generate_html(self, resume, template_name="modern"):
        """Generate HTML for resume"""
        try:
            template = self.env.get_template(f"{template_name}.html")
            
            # Prepare data for template
            template_data = self._prepare_template_data(resume)
            
            # Render HTML
            html = template.render(**template_data)
            
            return html
        except Exception as e:
            print(f"Error generating HTML: {e}")
            raise
    
    def generate_pdf(self, resume, template_name="modern"):
        """Generate PDF for resume"""
        try:
            # Generate HTML
            html = self.generate_html(resume, template_name)
            
            # Convert to PDF
            pdf_options = {
                'page-size': 'Letter',
                'margin-top': '0.5in',
                'margin-right': '0.5in',
                'margin-bottom': '0.5in',
                'margin-left': '0.5in',
                'encoding': "UTF-8",
                'no-outline': None,
                'quiet': ''
            }
            
            pdf_bytes = pdfkit.from_string(html, False, options=pdf_options)
            
            return pdf_bytes
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise
    
    def _prepare_template_data(self, resume):
        """Prepare data for the template"""
        # Format dates
        for section in ["education", "experience", "certifications"]:
            for item in resume.get(section, []):
                if item.get("start_date"):
                    item["start_date_formatted"] = self._format_date(item["start_date"])
                if item.get("end_date"):
                    item["end_date_formatted"] = self._format_date(item["end_date"])
                elif section == "experience" and item.get("current"):
                    item["end_date_formatted"] = "Present"
        
        # Get visible sections and their order
        visible_sections = []
        section_settings = resume.get("section_settings", [])
        
        if section_settings:
            for section in sorted(section_settings, key=lambda x: x.get("order", 999)):
                if section.get("visible", True):
                    visible_sections.append(section["name"])
        else:
            # Default order if no settings provided
            visible_sections = [
                "personal_info", "summary", "experience", "education", 
                "skills", "projects", "achievements", "certifications",
                "extracurriculars", "courses", "volunteer_work", "publications"
            ]
        
        # Add visible status to the data
        template_data = {
            "resume": resume,
            "visible_sections": visible_sections,
            "generated_date": datetime.now().strftime("%B %d, %Y")
        }
        
        return template_data
    
    def _format_date(self, date_obj):
        """Format date object as string"""
        if isinstance(date_obj, str):
            return date_obj
        
        try:
            return date_obj.strftime("%B %Y")
        except:
            return str(date_obj)