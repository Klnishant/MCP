import os
from groq import Groq
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_insigths(prompt):

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "you are a helpfull system agent analyze my data and give me a response"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content