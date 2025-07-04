import os
from euriai import EuriaiClient
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("EURI_API_KEY")
client = EuriaiClient(api_key=api_key, model="gpt-4.1-nano")

def generate_question(chapter_title, text):
    prompt = """
You are an expert educator. Based on the chapter "{chapter_title}", generate:
- 2 Remember-level questions
- 2 Understand-level questions
- 2 Apply-level questions
- 2 Analyze-level questions
- 2 Evaluate-level questions
- 2 Create-level questions

Chapter content:
{text[:3000]}
"""

    try:
        response = client.generate_completion(
            prompt=prompt,
            temperature=0.7,
        )
        return response
    except Exception as e:
        print("❌ Error generating Bloom questions:", e)
        return "❌ Failed to generate Bloom questions from EURI."