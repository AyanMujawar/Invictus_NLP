# The Auditor — EU MDR Compliance Checker

The Auditor is an AI-powered compliance tool that checks Medical Device Clinical Evaluation Reports (CER) against the EU MDR (Regulation 2017/745) guidelines. It is designed to help medical device manufacturers and regulatory auditors quickly identify compliance gaps, missing requirements, and safety issues — without manually going through hundreds of pages of regulations.

---

## What It Does

When you upload a Clinical Evaluation Report (PDF), the tool reads through it, compares each section against the official EU MDR guidelines, and highlights exactly where the document falls short. Every issue is tied to a specific regulation clause, given a severity rating, and comes with a suggested fix.

At the end, you get a readiness score out of 100 and a downloadable HTML report summarizing all findings.

---

## Key Features

- Checks your document against real EU MDR regulatory clauses
- Groups issues into categories like Risk Management, Clinical Evaluation, Post-Market Surveillance, and more
- Scores the document from 0 to 100 based on how many gaps were found
- Shows AI confidence level for each finding
- Generates a clean, downloadable audit report in HTML format
- Simple, modern web interface — no technical knowledge required to use

---

## How It Works

1. You upload a PDF Clinical Evaluation Report through the web interface.
2. The app splits the document into readable sections.
3. For each section, it finds the most relevant EU MDR guideline clauses.
4. An AI model (Groq's Llama 3.3-70B) analyzes the section and identifies any violations or missing items.
5. Results are organized, scored, and displayed on the dashboard.

---

## Setup Instructions

These steps assume you have Python installed on your machine (version 3.9 or higher recommended).

**Step 1 — Clone the repository**

If you haven't already, download the project to your local machine:

```bash
git clone https://github.com/AyanMujawar/Invictus_NLP.git
cd Invictus_NLP
```

**Step 2 — Create a virtual environment**

This keeps the project's dependencies isolated from your system Python:

```bash
python -m venv venv
venv\Scripts\activate
```

On Mac or Linux, use `source venv/bin/activate` instead.

**Step 3 — Install the required libraries**

```bash
pip install -r requirements.txt
```

**Step 4 — Set up your API key**

This project uses the Groq API to run the AI model. You need a free Groq API key from [console.groq.com](https://console.groq.com).

Create a file named `.env` in the root of the project folder and add the following line:

```
OPENAI_API_KEY=your_groq_api_key_here
```

**Step 5 — Run the application**

```bash
streamlit run app.py
```

Once the server starts, Streamlit will automatically open the app in your default browser. If it does not open on its own, look for the Local URL printed in your terminal (it will look like `http://localhost:8501`) and open it manually.

---

## Project Structure

| File | Purpose |
|---|---|
| `app.py` | Main web application and UI |
| `auditor.py` | AI auditing logic using the Groq API |
| `ingest.py` | PDF text extraction and chunking |
| `retriever.py` | Semantic search over guideline chunks |
| `report.py` | HTML report generation |
| `schema.py` | Data models for findings and reports |
| `data/guideline.pdf` | The EU MDR guideline document used as reference |

---

## Notes

- The `data/guideline.pdf` file must be present for the audit to run. It contains the reference EU MDR guidelines the AI compares against.
- The free tier of the Groq API has a daily token limit. If you hit a rate limit error, wait a few hours or create a new free account at [console.groq.com](https://console.groq.com).
- Only PDFs with selectable text (not scanned images) are supported. If your PDF is scanned, run it through an OCR tool first.