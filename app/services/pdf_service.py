import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

#Function to clean Markdown style text for proper PDF formatting
def clean_markdown_for_pdf(text: str) -> str:
    text = re.sub(r'\\(.+?)\\', r'\1', text)
    text = re.sub(r'#+\s*', '', text)
    text = text.replace("\n\n", "<br/><br/>")
    text = text.replace("\n", "<br/>")
    return text

#Function to generate a PDF report
def generate_pdf(summary: str, participants: list, pdf_path="report_output.pdf"):
    
    print("Generating PDF report...", flush=True)
    # Create the PDF document and set up styles
    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()
    
    # Customize 
    title_style = styles["Title"]
    title_style.fontSize = 16
    title_style.spaceAfter = 20
    #The content of the PDF
    elements = [
        Paragraph("MEETING REPORT", title_style),
        Spacer(1, 12),
        Paragraph(f"Participants: {', '.join(participants)}", styles["Normal"]),
        Spacer(1, 20),
        Paragraph(clean_markdown_for_pdf(summary), styles["Normal"]),
    ]
    
    doc.build(elements)
    print("Report generated :", pdf_path, flush=True)
    return pdf_path