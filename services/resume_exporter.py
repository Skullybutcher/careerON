from flask import render_template
from weasyprint import HTML
import os

class ResumeExporter:
    def __init__(self, ats_mode=True):
        self.ats_mode = ats_mode

    def export_resume_pdf(self, resume):
        """
        Export resume as PDF using an ATS-friendly or stylized HTML template.
        """
        template_name = 'ats_resume.html' if self.ats_mode else 'pretty_resume.html'
        html = render_template(template_name, resume=resume)
        pdf = HTML(string=html).write_pdf()
        return pdf

# Example usage:
# exporter = ResumeExporter(ats_mode=True)
# pdf_bytes = exporter.export_resume_pdf(resume_data)
# with open('resume_ats.pdf', 'wb') as f:
#     f.write(pdf_bytes)
