# 🛡️ The Auditor — EU MDR Compliance Checker

**The Auditor** is an AI-powered compliance dashboard designed to check Medical Device Clinical Evaluation Reports (CER) against the official **EU MDR (Regulation 2017/745)** guidelines. 

It helps medical device manufacturers and regulatory auditors instantly identify compliance gaps, safety hazards, and missing details, reducing manual audit preparation time by up to 80%.

---

## 🌟 Key Features

*   **Premium Compliance Dashboard**: A modern, clean user interface designed for clinical and regulatory workflows.
*   **AI-Powered Audits**: Uses advanced LLM agents (powered by Groq's Llama-3.3-70B model) to compare your report against regulatory guidelines.
*   **Dynamic Readiness Score**: Provides a clear compliance readiness percentage (out of 100) based on the severity of violations found.
*   **Automatic Categorization**: Groups issues into regulatory categories (e.g., *Clinical Evaluation, Risk Management, Post-Market Surveillance, Safety*) with custom suggested fixes.
*   **Clause Grounding**: Every identified gap is directly linked and referenced to the exact clause in the EU MDR guidelines.
*   **Confidence Indicators**: Shows AI confidence scoring for every finding.
*   **Exportable Reports**: Download structured compliance audit reports as highly styled, standalone HTML files with a single click.

---

## ⚙️ How It Works (Under the Hood)

1.  **Extract & Chunk**: The application extracts selectable text from your uploaded CER PDF and splits it into logical sections.
2.  **Semantic Search**: It queries the regulatory database to retrieve the most relevant matching clauses from the EU MDR guidelines.
3.  **AI Analysis**: The AI agent analyzes each section alongside the corresponding regulations, looking for missing requirements or compliance violations.
4.  **Report Generation**: Results are parsed, scored, and loaded into the interactive dashboard with charts showing severity and category distributions.

---

## 🚀 How to Run the Project

### 1. Set Up Virtual Environment
Open your terminal in the project directory and run:
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies
Install all required libraries:
```bash
pip install -r requirements.txt
```

### 3. Add API Keys
Create a file named `.env` in the root of the project directory and add your API key:
```env
OPENAI_API_KEY=your_groq_api_key_here
```
*(Note: You can name the variable either `OPENAI_API_KEY` or `GROQ_API_KEY`. The system will automatically detect and load whichever is set).*

### 4. Start the Application
Run the Streamlit server:
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser to start auditing!