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



def generate_transcription_pdf(transcription: str, participants: list, pdf_path="transcription_output.pdf"):
    """Generate a clean PDF containing only the full transcription with speakers"""
    print("Generating transcription PDF...", flush=True)
    
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    
    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()
    
    # Styles
    title_style = styles["Title"]
    title_style.fontSize = 18
    title_style.spaceAfter = 20
    
    heading_style = styles["Heading2"]
    heading_style.fontSize = 14
    heading_style.spaceAfter = 12
    
    # Clean transcription text for PDF
    clean_text = transcription.replace("\n", "<br/>")
    
    elements = [
        Paragraph("MEETING TRANSCRIPTION", title_style),
        Spacer(1, 12),
        Paragraph(f"<b>Participants:</b> {', '.join(participants)}", styles["Normal"]),
        Spacer(1, 30),
        Paragraph("FULL TRANSCRIPT", heading_style),
        Spacer(1, 10),
        Paragraph(clean_text, styles["BodyText"]),
    ]
    
    doc.build(elements)
    print(f"Transcription PDF generated: {pdf_path}", flush=True)
    return pdf_path