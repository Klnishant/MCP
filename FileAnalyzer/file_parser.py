import pandas as pd
import pymupdf 

def parse_csv(file_path):
    df = pd.read_csv(file_path)
    return df

def parse_excel(file_path):
    df = pd.read_excel(file_path)
    return df

def parse_pdf(file_path):
    pdf = pymupdf.open(file_path)
    text = "\n".join([page.get_text() for page in pdf])
    return text
