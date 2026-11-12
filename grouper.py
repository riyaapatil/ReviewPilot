# grouper.py
import json
from analyzer import client
from extractor import PaperInfo

def group_papers(papers: list[PaperInfo]) -> dict[str, list[int]]:
    summaries = []
    for i, p in enumerate(papers):
        summaries.append(f"[{i}] Title: {p.title}\nObjective: {p.objective}\nMethod: {p.methodology}")

    prompt = f"""Group these papers into 2-3 research themes based on their objectives and methods.
Return ONLY valid JSON in this format: {{"Theme Name 1": [0, 2], "Theme Name 2": [1, 3]}}

Papers:
{chr(10).join(summaries)}"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b", # Updated Groq model
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0
    )
    return json.loads(response.choices[0].message.content)