from fastapi import FastAPI
from pydantic import BaseModel
from tools.diagnosis_tools import get_diagnosis
from tools.symptom_extractor import extract_symptoms
from tools.pubmed_fetcher import fetch_pubmed_articles_with_metadata
from tools.summarizer import summarize_text

app = FastAPI()

class SymptomInput(BaseModel):
    description:str

@app.post("/diagnosis")
def diagnose_patient(data:SymptomInput):
    symptoms = extract_symptoms(data.description)
    diagnosis = get_diagnosis(symptoms)
    pwbmed_raw = fetch_pubmed_articles_with_metadata(" ".join(symptoms))
    summary = summarize_text(pwbmed_raw[:3000])
    
    return {
        "symptom":symptoms,
        "diabnosis":diagnosis,
        "pubmed_summary" :summary
    }
    