import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from schema import Finding

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

SEVERITY_WEIGHT = {
    "Critical": 25,
    "High": 12,
    "Medium": 5,
    "Low": 2
}

SYSTEM = """
You are a senior regulatory auditor specializing in EU MDR compliance.

You compare clinical study protocols against MDR guidelines.

Your task:
- Find compliance violations
- Find missing requirements
- Find safety gaps
- Find timing/date issues
- Find unclear responsibilities

Return ONLY valid JSON.
"""

def audit_section(section_text: str, guideline_clauses: str):

    prompt = f"""
Audit the following protocol section.

PROTOCOL SECTION:
{section_text}

RELEVANT GUIDELINES:
{guideline_clauses}

Return ONLY valid JSON in this format:

{{
  "findings": [
    {{
      "violating_statement": "...",
      "guideline_clause": "...",
      "severity": "Low",
      "explanation": "...",
      "confidence": 0.9,
      "suggested_correction": "..."
    }}
  ]
}}

If there are no violations:

{{"findings":[]}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        # Remove markdown code fences
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

        data = json.loads(content)

        findings = []

        for item in data.get("findings", []):
            try:
                findings.append(Finding(**item))
            except Exception:
                continue

        return findings

    except Exception as e:
        print("Audit error:", e)
        return []


def readiness_score(findings):

    penalty = sum(
        SEVERITY_WEIGHT.get(f.severity, 0)
        for f in findings
    )

    return max(0, 100 - penalty)