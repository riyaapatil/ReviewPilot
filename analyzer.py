# analyzer.py
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from extractor import PaperInfo

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client using OpenAI library
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """You are an expert research paper analyzer. Extract structured information from the provided text.
If a specific field (like dataset, venue, advantages, or limitations) is not explicitly reported, set it to null. Never invent information.
Return ONLY valid JSON matching this exact schema:
{
  "title": "string",
  "authors": "string (comma separated)",
  "publication_year": "string (e.g., '2024')",
  "publication_venue": "string or null (e.g., 'ACL', 'arXiv', 'IEEE')",
  "technologies_used": "string (comma separated list of models, frameworks, algorithms used)",
  "objective": "string",
  "methodology": "string",
  "dataset": "string or null",
  "key_findings": "string (bullet points of main results)",
  "advantages": "string or null (pros of the approach)",
  "limitations": "string or null (cons or gaps mentioned)"
}"""

def analyze_paper(text: str) -> PaperInfo:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b", # Updated Groq model
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze this paper:\n\n{text}"}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    
    content = response.choices[0].message.content
    
    try:
        data = json.loads(content)
        return PaperInfo(**data)
    except Exception as e:
        print(f"Error parsing JSON from Groq: {e}")
        print(f"Raw output: {content}")
        raise e