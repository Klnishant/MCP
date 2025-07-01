from fastmcp import FastMCP
from tools.diagnosis_tools import get_diagnosis
from tools.symptom_extractor import extract_symptoms
from tools.pubmed_fetcher import fetch_pubmed_articles_with_metadata
from tools.summarizer import summarize_text

mcp = FastMCP()

@mcp.tool()
def diagnose_patient(SymptomInput):
    symptoms = extract_symptoms(SymptomInput)
    diagnosis = get_diagnosis(symptoms)
    pwbmed_raw = fetch_pubmed_articles_with_metadata(" ".join(symptoms))
    summary = summarize_text(pwbmed_raw[:3000])
    
    return {
        "symptom":symptoms,
        "diabnosis":diagnosis,
        "pubmed_summary" :summary
    }

if __name__ == "__main__":
    mcp.run()