import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()
import sys

sys.stdout.reconfigure(encoding='utf-8')

EURI_API_URL = "https://api.euron.one/api/v1/euri/alpha/chat/completions"
EURI_API_KEY = os.getenv("EURI_API_KEY")

def classify_ticket(text: str) -> dict:
        prompt = f"""
You are a smart support ticket classifier.

Given a customer ticket, classify it into:
- Sentiment: Positive, Negative, Neutral
- Issue Type: Billing, Technical, Login, General, Other

Respond ONLY with a JSON object like this:
{{
    "sentiment": "Negative",
    "issue_type": "Billing"
}}

Customer Ticket:
\"\"\"{text}\"\"\""""

        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {EURI_API_KEY}"
        }

        payload = {
                "model": "gpt-4.1-nano",
                "messages": [
                        {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.3
        }
        
        try:
                response = requests.post(EURI_API_URL, headers=headers, json=payload)
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                parsed_result = json.loads(content)

                return({
                        "sentiment": parsed_result.get("sentiment", "Unknown"),
                        "issue_type": parsed_result.get("issue_type", "Genral")
                })
        except Exception as e:
                print(f"An error occurred: {e}")
                return({"sentiment": "Unknown", "issue_type": "Genral"})