import os
import requests
from dotenv import load_dotenv
from fpdf import FPDF
import unicodedata

load_dotenv()

EURI_API_KEY = os.getenv("EURI_API_KEY")


def clean_text_for_pdf(text: str):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

def generate_swot_report(info, sentiment):
    prompt = f"""
    Create a SWOT analysis of the company with this context:
    🔸 Company: {info.get('shortname')}
    🔸 Sector: {info.get('sector')}
    🔸 Market Cap: {info.get('marketcap')}
    🔸 Summary: {info.get('logBuisnessSummary')}
    🔸 Real-time Sentiment: {sentiment}

    Format it with clear headings:
    Strengths:
    Weaknesses:
    Opportunities:
    Threats:
    """

    payload = {
        "model": "gpt-4.1-nano",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 700,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {EURI_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.euron.one/api/v1/euri/alpha/chat/completions",
        headers=headers,
        json=payload
    )

    return response.json()["choices"][0]["message"]["content"]

def save_swot_pdf(swot_text: str, filename="swot_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    clean_text = clean_text_for_pdf(swot_text)

    for line in clean_text.split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf.output(filename)
    return filename