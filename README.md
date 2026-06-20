# The Auditor — EU MDR Compliance Checker
Audits a Clinical Evaluation Report against EU MDR (Reg. 2017/745),
citing the exact clause for every violation.

## Run
1. python -m venv venv  then  venv\Scripts\activate
2. pip install -r requirements.txt
3. Add GROQ_API_KEY=... to a file named .env
4. streamlit run app.py   (choose "Use sample data" to demo without a key)

## How it works
PDF -> split into chunks -> match each chunk to the right MDR rule
-> AI checks for violations -> score -> downloadable report.