# generator.py
from analyzer import client
from extractor import PaperInfo

def generate_section(theme_name: str, papers: list[PaperInfo]) -> str:
    context = ""
    for i, p in enumerate(papers):
        context += f"""
[Paper {i+1}] {p.title} by {p.authors} ({p.publication_year})
Objective: {p.objective}
Methodology: {p.methodology}
Findings: {p.key_findings}
Limitations: {p.limitations or 'Not reported'}
"""

    prompt = f"""Write a literature review paragraph for the theme: "{theme_name}".
Use ONLY the information provided below. Cite papers as [Paper 1], [Paper 2], etc.
Do not add external knowledge. Be concise and academic.

{context}"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b", # Updated Groq model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content