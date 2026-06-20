import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from schema import Finding

def get_client():
    # Force reload environment variables on demand
    load_dotenv(override=True)
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    return OpenAI(
        api_key=api_key,
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

      "category": "...",

      "severity": "Low",
      "explanation": "...",
      "confidence": 0.9,
      "suggested_correction": "..."
    }}
  ]
}}

category must be exactly one of:

- Clinical Evaluation
- Risk Management
- Post Market Surveillance
- Verification & Validation
- Equivalence
- Safety
- Regulatory Documentation
- Clinical Investigation
- Other

Category guidance:

Clinical Evaluation:
- systematic literature review
- clinical evidence
- clinical data appraisal
- clinical performance
- clinical evaluation reports
- clinical investigations

Risk Management:
- benefit-risk analysis
- risk assessment
- hazard identification
- residual risks
- risk controls
- risk acceptability
- adverse events
- contraindications
- undesirable side effects

Post Market Surveillance:
- PMS
- PMCF
- vigilance
- trend analysis
- incident monitoring
- post-market data collection

Verification & Validation:
- testing
- verification
- validation
- biocompatibility
- performance testing
- design verification

Equivalence:
- technical equivalence
- biological equivalence
- clinical equivalence
- equivalence justification

Safety:
- sterilization
- warnings
- precautions
- patient safety
- safety information

Regulatory Documentation:
- labeling
- instructions for use (IFU)
- device description
- required MDR documentation
- regulatory records

Clinical Investigation:
- study design
- endpoints
- patient enrollment
- clinical study methodology

Choose the SINGLE BEST category only.
Do not invent categories.

If there are no violations:

{{"findings":[]}}
"""

    try:
        client = get_client()
        model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
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
        raise e


def readiness_score(findings):

    severity_weights = {
        "Low": 5,
        "Medium": 10,
        "High": 15,
        "Critical": 20
    }

    category_severity = {}

    for f in findings:

        current = category_severity.get(
            f.category,
            0
        )

        category_severity[f.category] = max(
            current,
            severity_weights[f.severity]
        )

    penalty = sum(
        category_severity.values()
    )

    return max(0, 100 - penalty)