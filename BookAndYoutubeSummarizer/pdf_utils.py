import pymupdf
import re

def extract_chapters(pdf_path):
    doc = pymupdf.open(pdf_path)
    chapters = {}
    current_chapter = "Introduction"
    content = ""

    for page in doc:
        text = page.get_text()
        headings = re.findall(r'Chapter\s\d+\s*[:\-]?\s*(.*)', text, re.IGNORECASE)
        if headings:
            chapters[current_chapter] = content.strip()
            current_chapter = headings[0].strip()
            content = ""
        content += text + "\n"

    chapters[current_chapter] = content.strip()
    return chapters